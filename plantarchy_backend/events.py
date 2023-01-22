from datetime import datetime
from flask import request
from flask_socketio import SocketIO, send, emit
from .globals import g_gameloops, g_socket_map

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('disconnect')
def handle_disconnect():
    print(request.sid)
    id = g_socket_map[request.sid]
    socketio.emit(f"disconnect_player", {
        "id": id
    })
    del g_socket_map[request.sid]

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