import flask

from src.main import init

app = flask.Flask(__name__)
init(app)
