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

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from pymdownx.highlight import HighlightExtension, Highlight

FORMATTER = HtmlFormatter(nowrap=True)


class TemplateHighlight(Highlight):

    @staticmethod
    def get_linenos(code: str):
        """
        Generate line numbers for code block.
        """
        return Markup("\n".join(map(str, range(1, code.count("\n") + 2))))

    @staticmethod
    def _get_lexer(code: str, language: str | None, filename: str):
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

    @classmethod
    def highlight_code(cls,
                       code: str,
                       language: str | None = None,
                       filename: str | None = None):
        """
        Highlight block of code.
        This function is used in `source/code.html` template.
        """
        try:
            lexer = cls._get_lexer(code, language, filename or "")
        except ClassNotFound:
            lexer = TextLexer()

        return Markup(
            highlight(Markup(code.rstrip()).unescape(), lexer, FORMATTER))

    def highlight(self, src, language, *_args, **_kwargs):
        return flask.render_template(
            "source/code.html",
            source=src,
            language=language,
        )


class TemplateHighlightExtension(HighlightExtension):

    def get_pymdownx_highlighter(self):
        return TemplateHighlight


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
    Markdown(
        app,
        extensions=[
            'pymdownx.superfences',
            TemplateHighlightExtension(),
            'tables',
            TableWrapExtension(["table-box"]),
        ],
        extension_configs={},
    )

    app.jinja_env.globals.update(highlighter=TemplateHighlight)
