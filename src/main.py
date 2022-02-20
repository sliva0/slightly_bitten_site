from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import flask as flask
from werkzeug.exceptions import HTTPException

from flaskext.markdown import Markdown

from src import highlight, cookie_parser

DIRECTORY_DESCRIPTION_FILE_NAME = ".about.html"

CONTENT_SUFFIXES = ("", ".html")
SOURCE_SUFFIXES = ("", ".html", ".css", ".js", ".py")

PROJECT_PATH = Path(__file__).parent.parent


@dataclass
class RequestPath:
    _path: List[str] = field(default_factory=list)
    is_not_found: bool = False

    @staticmethod
    def join_link(path: List[str]):
        return "/" + "/".join(path) if path else ""

    @property
    def breadcrumbs_links(self):
        current_path = []
        for name in self._path:
            current_path.append(name)
            yield name, self.join_link(current_path)

    @property
    def path(self):
        return self.join_link(self._path)

    @property
    def parent(self):
        return self.join_link(self._path[:-1])

    @property
    def page_name(self):
        return self._path[-1]

    def add(self, name):
        self._path.append(name)

    @staticmethod
    def set_request_path():
        flask.g.rpath = RequestPath()


def test_all_suffixes(path: Path):
    for suffix in (path.suffix, ) + CONTENT_SUFFIXES:
        if (spath := path.with_suffix(suffix)).exists():
            return spath

    return None


def walk_subpath(path: Path, subpath: str):
    subpath_names = filter(bool, subpath.split("/"))

    for name in subpath_names:
        flask.g.rpath.add(name)

        if name.startswith(".") or name.startswith("__"):
            flask.abort(404)

        if not (path := test_all_suffixes(path / name)):
            flask.abort(404)

    return path


def load_file_template(path: Path):
    suffix = path.suffix
    with open(path) as file:
        source = file.read()

    if suffix == ".html":
        return flask.render_template_string(source)

    else:
        raise TypeError(f"I don't know how to show {suffix} files")


def load_source_file_template(path: Path):
    suffix = path.suffix
    with open(path) as file:
        source = file.read()

    if suffix in SOURCE_SUFFIXES:
        return flask.render_template("source_file.html", source=source, filename=path.name)

    else:
        raise TypeError(f"I don't know how to show {suffix} files")


def add_folder_files_in_global(path: Path, source: bool = False):
    suffixes = SOURCE_SUFFIXES if source else CONTENT_SUFFIXES
    files = []
    for file in path.iterdir():
        if file.name.startswith(".") or file.name.startswith("__"):
            continue

        if file.suffix in suffixes:
            files.append(file)

    flask.g.files = files


def file_finder(subpath: str = ""):
    path = walk_subpath(PROJECT_PATH / "content", subpath)

    if path.is_dir():
        path /= ".about.html"
        if not path.exists():
            flask.abort(404)
        add_folder_files_in_global(path.parent)

    return load_file_template(path)


def source_file_finder(subpath: str = ""):
    flask.g.rpath.add("source")
    path = walk_subpath(PROJECT_PATH, subpath)

    if path.is_dir():
        add_folder_files_in_global(path, source=True)
        return flask.render_template("source_folder.html")

    return load_source_file_template(path)


def index():
    return file_finder("")


def source_root():
    return source_file_finder("")


def error404_handler(_):
    if rp := flask.g.get("rpath"):
        rp.is_not_found = True

    return flask.render_template("not_found_error.html"), 404


def error_handler(error):
    return flask.render_template("error.html", error=error), error.code


def init(app: flask.Flask):
    highlight.init(app)
    cookie_parser.init(app)
    Markdown(app)

    app.jinja_env.globals.update(
        FOLDER_EMOJI='\U0001f4c2',
        FILE_EMOJI='\U0001f4c4',
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.before_request(RequestPath.set_request_path)

    app.add_url_rule('/', view_func=lambda: file_finder())
    app.add_url_rule('/<path:subpath>', view_func=file_finder)

    app.add_url_rule('/source', view_func=source_root)
    app.add_url_rule('/source/<path:subpath>', view_func=source_file_finder)

    app.register_error_handler(404, error404_handler)
    app.register_error_handler(HTTPException, error_handler)