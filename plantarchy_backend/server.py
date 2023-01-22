import flask
from flask import request
from flask_cors import CORS
import psycopg
from .events import socketio, update_tile, update_new_player
from . import db
from .globals import g_gameloops, g_socket_map, g_player_uuid_refcount
from .gameloop import Gameloop, create_game, GRIDSIZE, AlreadyOwnedError, NoPlayerError, NoSeedsError

app = flask.Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})
db.create_tables()

for loop in db.get_games():
    g_gameloops[loop["id"]] = Gameloop(loop["id"], loop["passcode"], loop["tileset"])
gameloop = create_game("ABCDABCD")
print("gameloop", g_gameloops)
db.create_game(gameloop)
gameloop.start()
socketio.init_app(app)

@app.route("/")
def root():
    return "Plantarchy Server 1.0.0 OK"

@app.route("/games")
def games():
    return flask.jsonify({
        "games": [loop.to_json() for loop in g_gameloops.values()]
    })

@app.route("/get_users")
def users():
    game_id = request.args.get("game_id")
    if game_id not in g_gameloops:
        return flask.jsonify({
            "error": "Game not found"
        }), 404
    game = g_gameloops[game_id]
    return flask.jsonify([player.to_json() for player in game.players.values()])

@app.route("/check_game", methods=["POST"])
def login_game():
    global g_gameloops
    print("bameloop", g_gameloops)

    data = request.json
    if "game_code" not in data:
        return 400, flask.jsonify({
            "error": "Please provide passcode"
        })
    id = ""
    print([a.passcode for a in g_gameloops.values()])
    for gid, loop in g_gameloops.items():
        print(gid, loop)
        if loop.passcode == data["game_code"]:
            id = gid
            break
    else:
        return 404, flask.jsonify({
            "error": "Game not found"
        })
    return flask.jsonify({
        "game": id
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("DATA", data)
    required_keys = ["game_code", "player_name", "socket_sid"]
    for key in required_keys:
        if key not in data:
            return flask.jsonify({
                "error": "Please provide " + key
            }), 400
    print("BB", data["game_code"])
    game = None
    for gid, loop in g_gameloops.items():
        print(gid, loop)
        if loop.passcode == data["game_code"]:
            game = loop
            break
    else:
        return 404, flask.jsonify({
            "error": "Game not found"
        })
    id = ""
    for uid,name in game.players.items():
        if name.player_name == data["player_name"]:
            id = uid
    if id == "":
        id = game.add_user(data["player_name"])
    g_socket_map[data["socket_sid"]] = id
    if id not in g_player_uuid_refcount:
        g_player_uuid_refcount[id] = 0
    g_player_uuid_refcount[id] += 1
    update_new_player(id)

    return flask.jsonify({
        "game_id": game.game_uuid,
        "player": id
    })

@app.route("/get_tiles")
def get_tiles_q():
    game_id = request.args.get("game_id")
    if game_id not in g_gameloops:
        return flask.jsonify({
            "error": "Game not specified or not found"
        }), 404
    return flask.jsonify(g_gameloops[game_id].tileset())

@app.route("/pick_berry", methods=["POST"])
def pick_berry():
    data = request.json
    required_keys = ["game_uuid", "player_uuid", "x", "y"]
    for key in required_keys:
        if key not in data:
            return flask.jsonify({
                "error": "Please provide " + key
            }), 400
    if data["game_uuid"] not in g_gameloops:
        return flask.jsonify({
            "error": "Game not found"
        }), 404

    game = g_gameloops[data["game_uuid"]]
    player = game.players[data["player_uuid"]]
    if not (0 <= data["x"] < GRIDSIZE and 0 <= data["y"] < GRIDSIZE):
        return flask.jsonify({
            "error": "Tile not found"
        }), 404
    tile = game.tiles[data["y"]][data["x"]]
    # print("BERRY", tile.x, tile.y, tile.crop)
    if tile.crop != 4:
        # print("BERRYFAIL", tile.x, tile.y, tile.crop)
        return flask.jsonify({
            "error": "Tile is not a berry"
        }), 403
    if tile.owner != data["player_uuid"]:
        return flask.jsonify({
            "error": "Berry is not owned by you"
        }), 403
    tile.crop = 3
    player.berries += 1
    update_tile(game.game_uuid, tile)
    return flask.jsonify({
        "berries": player.berries
    }), 200


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
        if data["game_uuid"] not in g_gameloops:
            return flask.jsonify({
                "error": "Game not found"
            }), 404

        game = g_gameloops[data["game_uuid"]]
        if not (0 <= data["x"] < GRIDSIZE and 0 <= data["y"] < GRIDSIZE):
            return flask.jsonify({
                "error": "Tile not found"
            }), 404
        try:
            game.set_tile(data["x"], data["y"], data["crop"], data["player_uuid"])
        except AlreadyOwnedError:
            return flask.jsonify({
                "error": "tile owned by another player"
            }), 403
        except NoPlayerError:
            return flask.jsonify({
                "error": "No player found matching uuid"
            }), 404
        except NoSeedsError:
            return flask.jsonify({
                "error": "Out of seeds"
            }), 418
            
        tile = game.tiles[data["y"]][data["x"]]
        update_tile(game.game_uuid, tile)
        return flask.jsonify({
            "x_coord": tile.x,
            "y_coord": tile.y,
            "player_uuid": tile.owner,
            "crop": tile.crop,
        })

    except psycopg.IntegrityError:
        return flask.jsonify({
            "error": "Game ID or player ID was invalid"
        }), 404
