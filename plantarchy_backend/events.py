from datetime import datetime
from flask import request
from flask_socketio import SocketIO, send, emit
from .globals import g_player_gamemap, g_socket_map, g_player_timeout, g_gameloops

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on("ping")
def handle_ping(data):
    if "player_id" not in data:
        return
    if "game_id" not in data:
        return
    if data["game_id"] not in g_gameloops:
        return
    g_gameloops[data["game_id"]].player_timeouts[data["player_id"]] = 3

def update_tile(game_id, tile):
    # print({
    #     "x_coord": tile.x,
    #     "y_coord": tile.y,
    #     "player_uuid": tile.owner,
    #     "crop": tile.crop,
    # })
    socketio.emit(f"{game_id}/update_tile", {
        "x_coord": tile.x,
        "y_coord": tile.y,
        "player_uuid": tile.owner,
        "crop": tile.crop,
    })

def update_new_player(player_uuid):
    socketio.emit(f"new_player", {
        "id": player_uuid
    })

# def update_player(game_uuid, player):
#     socketio.emit(f"{game_uuid}/player_update", player.to_json())