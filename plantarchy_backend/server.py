import flask
from flask import request
from flask_cors import CORS
import psycopg
from .events import socketio
from .db import \
    db_conn, \
    create_tables, get_games, get_game, \
    get_user, create_user, get_game_by_uuid, get_user_by_uuid, \
    get_tile, get_tiles, set_tile, get_tile_by_uuid

app = flask.Flask(__name__)
CORS(app)
create_tables()
socketio.init_app(app)

@app.route("/")
def root():
    return "Plantarchy Server 1.0.0 OK"

@app.route("/games")
def games():
    return flask.jsonify({
        "games": get_games()
    })

@app.route("/check_game", methods=["POST"])
def login_game():
    data = request.json
    if "game_code" not in data:
        return 400, flask.jsonify({
            "error": "Please provide passcode"
        })
    game = get_game(data["game_code"])
    if game is None:
        return 404, flask.jsonify({
            "error": "Game not found"
        })
    return flask.jsonify({
        "game": game["id"]
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("DATA", data)
    required_keys = ["game_code", "player_name"]
    for key in required_keys:
        if key not in data:
            return flask.jsonify({
                "error": "Please provide " + key
            }), 400
    print("BB", data["game_code"])
    game = get_game(data["game_code"])
    if game is None:
        return flask.jsonify({
            "error": "Game not found"
        }), 404
        
    print(game)
    user = get_user(data["player_name"], game["id"])
    if user is None:
        create_user(data["player_name"], game["id"])
        user = get_user(data["player_name"], game["id"])

    return flask.jsonify({
        "game_id": game["id"],
        "player": user["id"]
    })

@app.route("/get_tiles")
def get_tiles_q():
    game_id = request.args.get("game_id")
    if not game_id or not get_game_by_uuid(game_id):
        return flask.jsonify({
            "error": "Game not specified or not found"
        }), 404
    return flask.jsonify(get_tiles(game_id))

@app.route("/set_tile", methods=["POST"])
def set_tile_q():
    data = request.json
    required_keys = ["crop", "game_uuid", "player_uuid", "x", "y"]
    for key in required_keys:
        if key not in data:
            return flask.jsonify({
                "error": "Please provide " + key
            }), 400
    try:
        tile = get_tile(data["x"], data["y"], data["game_uuid"])
        if tile is None:
            return flask.jsonify({
                "error": "Tile not found"
            }), 404
        print(tile)
        if tile is not None and tile["crop"] != 0:
            return flask.jsonify({
                "error": "Player has already planted that square"
            }), 403
        set_tile(data["crop"], data["player_uuid"], tile["id"])
        tile["crop"] = data["crop"]
        tile["player_uuid"] = data["player_uuid"]
        return flask.jsonify(tile)

    except psycopg.IntegrityError:
        return flask.jsonify({
            "error": "Game ID or player ID was invalid"
        }), 404
