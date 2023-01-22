from datetime import datetime
from flask import request
from flask_socketio import SocketIO, send, emit
from .globals import g_player_gamemap, g_socket_map, g_player_uuid_refcount

socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('disconnect')
def handle_disconnect():
    print(request.sid)
    print("GAMER", g_socket_map)
    id = g_socket_map[request.sid]
    if id not in g_player_uuid_refcount:
        g_player_uuid_refcount[id] = 0
    g_player_uuid_refcount[id] -= 1
    if g_player_uuid_refcount[id] <= 0:
        del g_player_uuid_refcount[id]
        print("FIRE DISCONNECT", id)
        socketio.emit(f"disconnect_player", {
            "id": id
        })
        g_player_gamemap[id].clear(id)
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