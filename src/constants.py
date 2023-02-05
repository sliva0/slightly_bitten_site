from pathlib import Path

DIR_DESCR_FILENAME = ".about.html"

CONTENT_SUFFIXES = [".html", ".j2"]
TEXT_SOURCE_SUFFIXES = [".html", ".j2", ".css", ".js", ".py", ".txt", ""]
SOURCE_SUFFIXES = TEXT_SOURCE_SUFFIXES + [".webm", ".png", ".svg"]

PYGMENTS_BUILTIN_STYLES = [
    "gruvbox-dark", "gruvbox-light", "github-dark", "vim", "algol",
    "friendly_grayscale", "monokai", "zenburn", "material", "one-dark",
    "default"
]

ROOT_DIR = Path(__file__).parent.parent
CODE_STYLES_DIR = ROOT_DIR / "static" / "css" / "code_styles"
