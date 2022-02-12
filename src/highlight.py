from jinja2.ext import Markup

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

FORMATTER = HtmlFormatter(nowrap=True)


def get_linenos(code: str):
    return Markup("\n".join(map(str, range(1, code.rstrip().count("\n") + 2))))


def highlight_code(code: str, language=None):
    if language:
        lexer = get_lexer_by_name(language)
    else:
        lexer = guess_lexer(code)

    return Markup(highlight(Markup(code.rstrip()).unescape(), lexer, FORMATTER))


def init(app):
    app.jinja_env.globals.update(
        get_linenos=get_linenos,
        highlight_code=highlight_code,
    )
