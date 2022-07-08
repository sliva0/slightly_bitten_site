from dataclasses import dataclass
import json
from pathlib import Path
from mimetypes import guess_type

import flask
from markupsafe import Markup

import src.constants as const

PROJECT_PATH = Path(__file__).parent.parent


def test_all_suffixes(path: Path, suffixes: list[str]) -> Path | None:
    """
    Tests different options of file suffix and check its validity.
    """
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


def walk_subpath(path: Path, subpath: str, suffixes: list[str], hidden_func=is_hidden) -> Path:
    """
    Iterates over directory names in path to find file.
    """
    subpath_names = filter(bool, subpath.split("/"))

    for name in subpath_names:
        flask.g.rpath.add(name)
        file = path / name

        if hidden_func(file):
            flask.abort(404)

        file = test_all_suffixes(file, suffixes)
        if not file:
            flask.abort(404)
        
        path = file

    return path


def guess_type_and_load_media(path: Path, file_link: str) -> str:
    """
    Loads media template for any media file.
    """
    mime_type, _ = guess_type(path)
    if not mime_type:
        mime_type = "invalid/invalid"

    return flask.render_template(
        "source/media.html",
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
    """
    Loads source (text or media) file template.
    """
    if path.suffix in const.TEXT_SOURCE_SUFFIXES:
        with open(path) as file:
            source = file.read()

        return flask.render_template("source/file.html", source=source, filename=path.name)

    file_link = "/raw/" + str(path.relative_to(PROJECT_PATH))
    return guess_type_and_load_media(path, file_link)


def is_hidden_source(file: Path) -> bool:
    return file.name.startswith("__") or (file.name.startswith(".") and file.is_dir())


def content_filter(file: Path) -> bool:
    return not is_hidden(file) and file.suffix in const.CONTENT_SUFFIXES


def source_filter(file: Path) -> bool:
    return not is_hidden_source(file) and file.suffix in ("", *const.SOURCE_SUFFIXES)


def content_file_finder(subpath: str = "") -> str:
    """
    Finds and loads content file template.
    """
    path = walk_subpath(PROJECT_PATH / "content", subpath, const.CONTENT_SUFFIXES)

    if path.is_dir():
        flask.g.rpath.scan_dir(path, content_filter)
        path /= const.DIR_DESCR_FILENAME
        if not path.exists():
            flask.abort(404)

    return load_content_file_template(path)


def source_file_finder(subpath: str = "") -> str:
    """
    Finds and loads source file template.
    """
    flask.g.rpath.add("source")
    path = walk_subpath(PROJECT_PATH, subpath, const.SOURCE_SUFFIXES, is_hidden_source)

    if path.is_dir():
        flask.g.rpath.scan_dir(path, source_filter)
        return flask.render_template("source/folder.html")
    else:
        return load_source_file_template(path)


def raw_file_finder(subpath: str):
    """
    Find and loads raw files directly from directories.
    """
    flask.g.rpath.add("raw")
    path = walk_subpath(PROJECT_PATH, subpath, const.SOURCE_SUFFIXES, is_hidden_source)

    if not path.is_file():
        flask.abort(404)

    mimetype = None
    if path.suffix in const.TEXT_SOURCE_SUFFIXES:
        mimetype = "text/plain"

    return flask.send_from_directory(
        PROJECT_PATH,
        path.relative_to(PROJECT_PATH),
        mimetype=mimetype,
    )


@dataclass
class Article:
    """
    Dataclass representing meta information about the article.
    """
    path: Path
    link: str
    file_content: str
    date: str = "YYYY.MM.DD"
    number: int = 0

    def __lt__(self, other: "Article") -> bool:
        return (self.date, self.number) < (other.date, other.number)

    @staticmethod
    def _load_meta_block(article: str):
        return json.loads(flask.render_template_string(article, article_mode="meta"))

    @classmethod
    def parse(cls, article_path: Path, link: Path | str) -> "Article":
        with article_path.open() as file:
            file_content = file.read()

        meta_info = cls._load_meta_block(file_content)

        return cls(article_path, "/" + str(link), file_content, **meta_info)

    def include(self, mode="preview") -> Markup:
        template = flask.render_template_string(
            self.file_content,
            link=self.link,
            article_mode=mode,
        )
        return Markup(template)


def get_articles(subpath: str = "/articles") -> list[Article]:
    """
    Finds all articles in directory and loads information about it.
    """
    suffixes = const.CONTENT_SUFFIXES
    root = PROJECT_PATH / "content"
    dir_path = walk_subpath(root, subpath, suffixes)
    article_list: list[Article] = []

    for file in dir_path.iterdir():
        if is_hidden(file):
            continue

        if file.is_file() and file.suffix in suffixes:
            article = Article.parse(file, file.relative_to(root))
        elif (about := file / const.DIR_DESCR_FILENAME).exists():
            article = Article.parse(about, file.relative_to(root))
        else:
            continue

        article_list.append(article)

    return sorted(article_list, reverse=True)
