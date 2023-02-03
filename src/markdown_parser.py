import copy

from flaskext.markdown import Markdown

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from src import code_highlight as code_hlt


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
            code_hlt.TemplateHighlightExtension(),
            'tables',
            TableWrapExtension(["table-box"]),
        ],
        extension_configs={},
    )

    app.jinja_env.globals.update(highlighter=code_hlt.TemplateHighlight)
