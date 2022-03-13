from jinja2.ext import Markup

from pygments import highlight

from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name, guess_lexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.lexers.special import TextLexer

from pygments.util import ClassNotFound
from pygments.formatters import HtmlFormatter

FORMATTER = HtmlFormatter(nowrap=True)


def get_linenos(code: str):
    return Markup("\n".join(map(str, range(1, code.rstrip().count("\n") + 2))))


def get_lexer(code: str, language: str, filename: str):
    if language:
        return get_lexer_by_name(language)

    if filename:
        if filename.endswith(".html"):
            return HtmlDjangoLexer()
        return guess_lexer_for_filename(filename, code)

    return guess_lexer(code)


def highlight_code(code: str, language: str | None = None, filename: str | None = None):
    try:
        lexer = get_lexer(code, language, filename)
    except ClassNotFound:
        lexer = TextLexer()

    return Markup(highlight(Markup(code.rstrip()).unescape(), lexer, FORMATTER))


def init(app):
    app.jinja_env.globals.update(
        get_linenos=get_linenos,
        highlight_code=highlight_code,
    )
