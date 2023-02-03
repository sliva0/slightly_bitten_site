import flask
from markupsafe import Markup

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, get_lexer_by_name, guess_lexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound

from pymdownx import highlight as hlt

from pygments.formatters import HtmlFormatter

FORMATTER = HtmlFormatter(nowrap=True)


class TemplateHighlight(hlt.Highlight):

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


class TemplateHighlightExtension(hlt.HighlightExtension):

    def get_pymdownx_highlighter(self):
        return TemplateHighlight