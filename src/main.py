from pathlib import Path

import flask
from werkzeug.exceptions import HTTPException

from flaskext.markdown import Markdown

from src import highlight, cookie_parser, request_path

DIRECTORY_DESCRIPTION_FILE_NAME = ".about.html"

CONTENT_SUFFIXES = (".html", )
SOURCE_SUFFIXES = (".html", ".css", ".js", ".py", ".webm", ".png", ".svg", ".txt")

PROJECT_PATH = Path(__file__).parent.parent


def test_all_suffixes(path: Path, suffixes: tuple[str]):
    if path.suffix in ("", *suffixes) and path.exists():
        return path

    for suffix in suffixes:
        if (spath := path.with_suffix(suffix)).exists():
            return spath

    return None


def is_hidden(name: str):
    return name.startswith(".") or name.startswith("__")


def walk_subpath(path: Path, subpath: str, suffixes: tuple[str]):
    subpath_names = filter(bool, subpath.split("/"))

    for name in subpath_names:
        flask.g.rpath.add(name)

        if is_hidden(name):
            flask.abort(404)

        path = test_all_suffixes(path / name, suffixes)

        if not path:
            flask.abort(404)

    return path


def load_file_template(path: Path):
    with open(path) as file:
        source = file.read()

    return flask.render_template_string(source)


def load_source_file_template(path: Path):
    with open(path) as file:
        source = file.read()

    return flask.render_template("source_file.html", source=source, filename=path.name)


def add_folder_files_in_global(path: Path, suffixes: tuple[str]):
    files = []

    for file in path.iterdir():
        if not is_hidden(file.name) and file.suffix in ("", *suffixes):
            files.append(file)

    flask.g.files = files


def file_finder(subpath: str = ""):
    suffixes = CONTENT_SUFFIXES

    path = walk_subpath(PROJECT_PATH / "content", subpath, suffixes)

    if path.is_dir():
        path /= ".about.html"
        if not path.exists():
            flask.abort(404)

        add_folder_files_in_global(path.parent, suffixes)

    return load_file_template(path)


def source_file_finder(subpath: str = ""):
    flask.g.rpath.add("source")
    suffixes = SOURCE_SUFFIXES

    path = walk_subpath(PROJECT_PATH, subpath, suffixes)

    if path.is_dir():
        add_folder_files_in_global(path, suffixes)
        
        if (about_path := path / ".about.html").exists():
            return load_file_template(about_path)

        return flask.render_template("source_folder.html")
    else:
        return load_source_file_template(path)


def error404_handler(_):
    if rp := flask.g.get("rpath"):
        rp.is_not_found = True

    return flask.render_template("not_found_error.html"), 404


def error_handler(error):
    return flask.render_template("error.html", error=error), error.code


def init(app: flask.Flask):
    highlight.init(app)
    cookie_parser.init(app)
    request_path.init(app)
    Markdown(app)

    app.jinja_env.globals.update(
        FOLDER_EMOJI='\U0001f4c2',
        FILE_EMOJI='\U0001f4c4',
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.add_url_rule('/', view_func=file_finder)
    app.add_url_rule('/<path:subpath>', view_func=file_finder)

    app.add_url_rule('/source', view_func=source_file_finder)
    app.add_url_rule('/source/<path:subpath>', view_func=source_file_finder)

    app.register_error_handler(404, error404_handler)
    app.register_error_handler(HTTPException, error_handler)