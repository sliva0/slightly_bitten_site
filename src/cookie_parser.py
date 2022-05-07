import re

import flask


def get_unique_elements(_list: list) -> list:
    """get unique elements of list without changing order"""
    return list(dict.fromkeys(_list))


def get_theme_names() -> list[str]:
    with open("./static/css/themes.css") as file:
        css_file = file.read()

    themes = re.findall(r"\n\.([a-z\-]+-theme)", css_file)

    return get_unique_elements(themes)


def to_bool_str(value: str) -> str:
    return BOOL_SET[not bool(value)]  # True -> "1", False -> ""


def set_cookie_value_after_this_request(name: str, value: str):
    @flask.after_this_request
    def set_cookie_value(response: flask.Response):
        response.set_cookie(name, value, samesite='Lax', expires=1 << 32 - 1)
        return response


def get_cookie_value(name: str, possible_values: list[str]) -> str:
    """first possible value - default"""

    value = flask.request.args.get(name)  # try to get cookie value from link args or form data
    if value is None:
        value = flask.request.form.get(name)

    if value is not None and value in possible_values:
        set_cookie_value_after_this_request(name, value)
        return value

    value = flask.request.cookies.get(name)
    if value is not None and value in possible_values:
        return value

    set_cookie_value_after_this_request(name, possible_values[0])
    return possible_values[0]


def process_cookies():
    flask.g.theme = get_cookie_value("theme", THEME_NAMES)
    flask.g.body_width = get_cookie_value("body_width", BODY_WIDTHS)

    for cookie_name in BOOL_COOKIE_LIST:
        flask.g.setdefault(cookie_name, get_cookie_value(cookie_name, BOOL_SET))

    flask.g.mode = THEME_MODES[bool(flask.g.dark_mode)]


THEME_NAMES = get_theme_names()
THEME_MODES = ("light-mode", "dark-mode")
BODY_WIDTHS = get_unique_elements(["40", *map(str, range(20, 101, 5))])

BOOL_SET = ["1", ""]  # [True, False]
BOOL_COOKIE_LIST = ("dark_mode", "use_js", "use_hl", "fonts", "extra_css")


def init(app: flask.Flask):
    app.before_request(process_cookies)

    app.jinja_env.globals.update(
        to_bool_str=to_bool_str,
        THEME_NAMES=THEME_NAMES,
        THEME_MODES=THEME_MODES,
    )
