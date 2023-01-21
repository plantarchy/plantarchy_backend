import flask
from flask import request
from .db import db_conn, create_tables, get_games, get_game

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

@app.route("/login_game", methods=["POST"])
def login_game():
    game = get_game()
    return flask.jsonify({
        game: game["id"]
    })