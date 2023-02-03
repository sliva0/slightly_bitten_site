import re
from pathlib import Path

import flask
from werkzeug.exceptions import HTTPException

from src import cookie_parser, request_path, file_finders, markdown_parser

PROJECT_PATH = Path(__file__).parent.parent


def error404_handler(_):
    if rp := flask.g.get("rpath"):
        rp.is_not_found = True

    return flask.render_template("error/not_found.html"), 404


def error_handler(error):
    return flask.render_template("error/base.html", error=error), error.code


def load_license_text():
    with (PROJECT_PATH / "LICENSE.txt").open() as file:
        # regexp to replace all single line breaks with spaces
        return re.sub("(.)\n(.)", r"\1 \2", file.read())


def add_redirect_rule(app: flask.Flask, from_path: str, to_path: str):

    @app.route(from_path)
    def _redirect():
        return flask.redirect(to_path)


def init(app: flask.Flask):
    markdown_parser.init(app)
    cookie_parser.init(app)
    request_path.init(app)

    app.jinja_env.globals.update(
        FOLDER_EMOJI='\U0001f4c2',
        FILE_EMOJI='\U0001f4c4',
        HOSTNAME="sliva0.mk",
        LICENSE_TEXT=load_license_text(),
        get_articles=file_finders.get_articles,
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    add_redirect_rule(app, '/favicon.ico', '/static/media/favicon.png')

    for path in ("/", "/<path:subpath>"):
        app.add_url_rule(
            path,
            methods=["GET", "POST"],
            view_func=file_finders.content_file_finder,
        )

    for path in ("/source/", "/source/<path:subpath>"):
        app.add_url_rule(
            path,
            view_func=file_finders.source_file_finder,
        )

    app.add_url_rule("/raw/<path:subpath>", view_func=file_finders.raw_file_finder)

    app.register_error_handler(404, error404_handler)
    app.register_error_handler(HTTPException, error_handler)
