from dataclasses import dataclass
import json
from pathlib import Path
from mimetypes import guess_type

import flask
from jinja2 import Markup

DIRECTORY_DESCRIPTION_FILE_NAME = ".about.html"

CONTENT_SUFFIXES = (".html", )
TEXT_SOURCE_SUFFIXES = (".html", ".css", ".js", ".py", ".txt", "")
SOURCE_SUFFIXES = TEXT_SOURCE_SUFFIXES + (".webm", ".png", ".svg")

PROJECT_PATH = Path(__file__).parent.parent


def test_all_suffixes(path: Path, suffixes: tuple[str]) -> Path | None:
    if path.suffix:  # if suffix is present
        if path.suffix in suffixes and path.exists():  # check its validity
            return path
        return None

    if path.exists():  # if suffix not present and file exists
        return path

    for suffix in suffixes:  # trying to find a suffix by brute force
        if (spath := path.with_suffix(suffix)).exists():
            return spath

    return None


def is_hidden(file: Path) -> bool:
    return file.name.startswith("__") or file.name.startswith(".")


def walk_subpath(path: Path, subpath: str, suffixes: tuple[str], hidden_func=is_hidden) -> Path:
    subpath_names = filter(bool, subpath.split("/"))

    for name in subpath_names:
        flask.g.rpath.add(name)
        file = path / name

        if hidden_func(file):
            flask.abort(404)

        if not (path := test_all_suffixes(file, suffixes)):
            flask.abort(404)

    return path


def guess_type_and_load_media(path: Path, file_link: str) -> str:
    mime_type, _ = guess_type(path)
    if not mime_type:
        mime_type = "invalid/invalid"

    return flask.render_template(
        "content/media.html",
        tag=mime_type.split("/")[0],
        file_link=file_link,
        mime_type=mime_type,
    )


def load_content_file_template(path: Path) -> str:
    with open(path) as file:
        source = file.read()

    # Place for the code for processing content files other than HTML
    return flask.render_template_string(source)


def load_source_file_template(path: Path) -> str:
    if path.suffix in TEXT_SOURCE_SUFFIXES:
        with open(path) as file:
            source = file.read()

        return flask.render_template("source/file.html", source=source, filename=path.name)

    file_link = "/" + str(path.relative_to(PROJECT_PATH))
    return guess_type_and_load_media(path, file_link)


def is_hidden_source(file: Path) -> bool:
    return file.name.startswith("__") or (file.name.startswith(".") and file.is_dir())


def content_filter(file: Path) -> bool:
    return not is_hidden(file) and file.suffix in CONTENT_SUFFIXES


def source_filter(file: Path) -> bool:
    return not is_hidden_source(file) and file.suffix in ("", *SOURCE_SUFFIXES)


def content_file_finder(subpath: str = "") -> str:
    suffixes = CONTENT_SUFFIXES

    path = walk_subpath(PROJECT_PATH / "content", subpath, suffixes)

    if path.is_dir():
        flask.g.rpath.scan_dir(path, content_filter)
        path /= DIRECTORY_DESCRIPTION_FILE_NAME
        if not path.exists():
            flask.abort(404)

    return load_content_file_template(path)


def source_file_finder(subpath: str = "") -> str:
    flask.g.rpath.add("source")
    suffixes = SOURCE_SUFFIXES

    path = walk_subpath(PROJECT_PATH, subpath, suffixes, is_hidden_source)

    if path.is_dir():
        flask.g.rpath.scan_dir(path, source_filter)
        return flask.render_template("source/folder.html")
    else:
        return load_source_file_template(path)


@dataclass()
class Article:
    path: Path
    link: str
    file_content: str
    date: str = "YYYY.MM.DD"
    number: int = 0

    def __lt__(self, other) -> bool:
        return (self.date, self.number) < (other.date, other.number)

    @staticmethod
    def _load_meta_block(article: str):
        return json.loads(flask.render_template_string(article, article_mode="meta"))

    @classmethod
    def parse(cls, article_path: Path, link: str) -> "Article":
        with article_path.open() as file:
            file_content = file.read()

        meta_info = cls._load_meta_block(file_content)

        return cls(article_path, link, file_content, **meta_info)

    def include(self, mode="preview", **kwargs) -> Markup:
        template = flask.render_template_string(
            self.file_content,
            link=self.link,
            article_mode=mode,
        )
        return Markup(template)


def get_articles(subpath: str = "/articles") -> list[Article]:
    suffixes = CONTENT_SUFFIXES
    root = PROJECT_PATH / "content"
    dir_path = walk_subpath(root, subpath, suffixes)
    article_list: list[Article] = []

    for file in dir_path.iterdir():
        if file.is_file() and not is_hidden(file) and file.suffix in suffixes:
            article = Article.parse(file, str(file.relative_to(root)))
            article_list.append(article)

    return sorted(article_list)
