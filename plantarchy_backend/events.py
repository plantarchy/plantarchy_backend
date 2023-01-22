from datetime import datetime
from flask_socketio import SocketIO, send, emit

socketio = SocketIO(cors_allowed_origins="*")

# @socketio.on("ping")
# def handle_ping(data):
#     print(f"Received ping from {data['player']}, ee")
#     send({ "response": "hello" }, json=True)

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