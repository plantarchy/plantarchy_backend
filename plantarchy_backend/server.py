import flask
from .db import db_conn, create_tables, get_games

app = flask.Flask(__name__)
create_tables()

@app.route("/")
def root():
    return "Plantarchy Server 1.0.0 OK"

@app.route("/games")
def games():
    return flask.jsonify({
        "games": get_games()
    })
