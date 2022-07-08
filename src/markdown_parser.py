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
    """
    Generate line numbers for code block.
    """
    return Markup("\n".join(map(str, range(1, code.rstrip().count("\n") + 2))))


def get_lexer(code: str, language: str | None, filename: str):
    """
    Choose the best suitable lexer depending on present information about code.
    """
    if language:
        return get_lexer_by_name(language)

    if filename.endswith((".html", ".j2")):
        return HtmlDjangoLexer()

    if filename:
        return guess_lexer_for_filename(filename, code)

    return guess_lexer(code)


def highlight_code(code: str, language: str | None = None, filename: str | None = None):
    """
    Highlight block of code.
    This function is used in `source/code.html` template.
    """
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
    """
    Wraps all `table` tags in a `div` tag with the given css classes.
    """
    classes: list[str]

    def run(self, root):
        """
        Turns all `table` tags into `div` tags and appends copy of the original table to it.
        """
        # root.iter is converted to a tuple to prevent an infinite loop
        # every iteration append new table tag
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
    # This is the easiest way that I found to change the html wrapper of a block of code
    # when the fenced_code extension is enabled.
    # FencedBlockPreprocessor always uses CodeHilite class directly from library,
    # ignoring the fact that the passed code highlighting extension can be a sub class.
    codehilite.CodeHilite = CodeHilite

    tw_extension = TableWrapExtension(["table-box"])
    Markdown(app, extensions=['fenced_code', 'codehilite', 'tables', tw_extension])

    app.jinja_env.globals.update(
        get_linenos=get_linenos,
        highlight_code=highlight_code,
    )
