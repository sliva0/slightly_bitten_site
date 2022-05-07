import copy

import flask
from markupsafe import Markup

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name, guess_lexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound
from pygments.formatters import HtmlFormatter

from flaskext.markdown import Markdown

from markdown.extensions import codehilite, Extension
from markdown.treeprocessors import Treeprocessor

FORMATTER = HtmlFormatter(nowrap=True)


def get_linenos(code: str):
    return Markup("\n".join(map(str, range(1, code.rstrip().count("\n") + 2))))


def get_lexer(code: str, language: str | None, filename: str):
    if language:
        return get_lexer_by_name(language)

    if filename.endswith((".html", ".j2")):
        return HtmlDjangoLexer()

    if filename:
        return guess_lexer_for_filename(filename, code)

    return guess_lexer(code)


def highlight_code(code: str, language: str | None = None, filename: str | None = None):
    try:
        lexer = get_lexer(code, language, filename or "")
    except ClassNotFound:
        lexer = TextLexer()

    return Markup(highlight(Markup(code.rstrip()).unescape(), lexer, FORMATTER))


class CodeHilite(codehilite.CodeHilite):
    def hilite(self, shebang=True):
        self.src = self.src.strip('\n')
        return flask.render_template("source/code.html", source=self.src, language=self.lang)


class TableWrapTreeprocessor(Treeprocessor):
    classes: list[str]

    def run(self, root):
        for block in tuple(root.iter("table")):
            table = copy.copy(block)
            block.clear()
            block.tag = "div"
            block.set("class", ''.join(self.classes))
            block.append(table)


class TableWrapExtension(Extension):
    def __init__(self, classes: list[str]):
        self.classes = classes

    def extendMarkdown(self, md):
        tp = TableWrapTreeprocessor(md)
        tp.classes = self.classes
        md.treeprocessors.register(tp, 'tablewrap', 30)
        md.registerExtension(self)


def init(app):
    # This is the easiest way to change the html wrapper of a block of code
    # when the fenced_code extension is enabled that I found
    codehilite.CodeHilite = CodeHilite

    tw_extension = TableWrapExtension(["table-box"])
    Markdown(app, extensions=['fenced_code', 'codehilite', 'tables', tw_extension])

    app.jinja_env.globals.update(
        get_linenos=get_linenos,
        highlight_code=highlight_code,
    )
