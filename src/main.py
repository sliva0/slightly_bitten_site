from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import flask as flask
from werkzeug.exceptions import HTTPException

from flaskext.markdown import Markdown

from src import highlight, cookie_parser

DIRECTORY_DESCRIPTION_FILE_NAME = ".about.html"
POSSIBLE_SUFFIXES = ("", ".html")
PROJECT_PATH = Path(__file__).parent.parent


@dataclass
class Breadcrumbs:
    path: List[str] = field(default_factory=list)
    is_not_found: bool = False

    @property
    def links(self):
        current_path = [""]
        for name in self.path:
            current_path.append(name)
            yield name, "/".join(current_path)

    def add(self, name):
        self.path.append(name)

    @staticmethod
    def set_breadcrumbs():
        flask.g.breadcrumbs = Breadcrumbs()


def test_all_suffixes(path: Path):
    for suffix in (path.suffix, ) + POSSIBLE_SUFFIXES:
        if (spath := path.with_suffix(suffix)).exists():
            return spath

    return None


def load_file_template(path: Path):
    suffix = path.suffix
    with open(path) as file:
        source = file.read()

    if suffix == ".html":
        return flask.render_template_string(source)

    else:
        raise TypeError(f"I don't know how to show {suffix} files")


def index():
    return file_finder("")


def file_finder(subpath: str = ""):
    path = PROJECT_PATH / "content"
    subpath = filter(bool, subpath.split("/"))

    for name in subpath:
        flask.g.breadcrumbs.add(name)

        if name.startswith("."):
            flask.abort(404)

        if not (path := test_all_suffixes(path / name)):
            flask.abort(404)

    if path.is_dir():
        path /= ".about.html"
        if not path.exists():
            flask.abort(404)

    return load_file_template(path)


def error404_handler(_):
    if bc := flask.g.get("breadcrumbs"):
        bc.is_not_found = True

    return flask.render_template("not_found_error.html"), 404


def error_handler(error):
    return flask.render_template("error.html", error=error), error.code


def init(app: flask.Flask):
    highlight.init(app)
    cookie_parser.init(app)
    Markdown(app)

    app.before_request(Breadcrumbs.set_breadcrumbs)

    app.add_url_rule('/', view_func=lambda: file_finder())
    app.add_url_rule('/<path:subpath>', view_func=file_finder)
    app.register_error_handler(404, error404_handler)
    app.register_error_handler(HTTPException, error_handler)