from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import flask as f
import werkzeug

from flaskext.markdown import Markdown

import highlight, cookie_parser

DIRECTORY_DESCRIPTION_FILE_NAME = ".about.html"
POSSIBLE_SUFFIXES = ("", ".html")

app = f.Flask(__name__)

highlight.init(app)
cookie_parser.init(app)
Markdown(app)

templates_path = Path(__file__).parent / "templates"


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


@app.before_request
def set_breadcrumbs():
    f.g.bc = Breadcrumbs()


@app.route('/')
def index():
    return template_finder("")


@app.route('/<path:subpath>')
def template_finder(subpath: str):
    path = templates_path / "content"
    subpath = filter(bool, subpath.split("/"))

    bc = f.g.bc

    for name in subpath:
        bc.add(name)

        if name.startswith("."):
            f.abort(404)

        file = path / name
        for suffix in POSSIBLE_SUFFIXES:
            if (spath := file.with_suffix(suffix)).exists():
                path = spath
                break
        else:
            f.abort(404)

        if path.is_file():
            break

    if path.is_dir():
        path /= ".about.html"
        if not path.exists():
            f.abort(404)

    return f.render_template(str(path.relative_to(templates_path)))


@app.errorhandler(404)
def not_found_page(_):
    if bc := f.g.get("bc"):
        bc.is_not_found = True

    return f.render_template("not_found_error.html"), 404


@app.errorhandler(werkzeug.exceptions.HTTPException)
def error_page(error):
    return f.render_template("error.html", error=error), error.code