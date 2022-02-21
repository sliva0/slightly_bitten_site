import re

import flask


def get_theme_names():
    with open("./static/css/themes.css") as file:
        css_file = file.read()

    themes = re.findall(r"\n\.(theme-[a-z\-]+)", css_file)
    
    return list(dict.fromkeys(themes))


def get_theme_type(inverted: bool = False):
    return THEME_TYPES[bool(flask.g.type_light) ^ inverted]


def invert_cookie_bool(value: str):
    return BOOL_SET[bool(value)]


def is_valid_value(value, possible_values: list):
    return value is not None and value in possible_values


def set_cookie_value_after_this_request(name: str, value: str):
    @flask.after_this_request
    def set_cookie_value(response):
        response.set_cookie(name, value)
        return response


def get_cookie_value(name: str, possible_values: list):
    """first possible value - default"""

    value = flask.request.args.get(name) # try to get cookie value from link args
    if is_valid_value(value, possible_values):
        set_cookie_value_after_this_request(name, value)
        return value

    value = flask.request.cookies.get(name)
    if is_valid_value(value, possible_values):
        return value
    else:
        set_cookie_value_after_this_request(name, possible_values[0])
        return possible_values[0]


def process_cookies():
    flask.g.theme = get_cookie_value("theme", THEME_NAMES)

    for cookie_name in BOOL_COOKIE_LIST:
        flask.g.setdefault(cookie_name, get_cookie_value(cookie_name, BOOL_SET))


THEME_NAMES = get_theme_names()
THEME_TYPES = ("type-dark", "type-light")
BOOL_SET = ("1", "")  # (True, False)
BOOL_COOKIE_LIST = ("type_light", "use_js", "use_hl", "fonts", "extra_css")


def init(app: flask.Flask):
    app.before_request(process_cookies)

    app.jinja_env.globals.update(
        get_theme_type=get_theme_type,
        invert_bool=invert_cookie_bool,
        THEME_NAMES=THEME_NAMES,
        THEME_TYPES=THEME_TYPES,
    )