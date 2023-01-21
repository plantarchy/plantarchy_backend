from datetime import datetime
from flask_socketio import SocketIO, send, emit

socketio = SocketIO(cors_allowed_origins="*")

# @socketio.on("ping")
# def handle_ping(data):
#     print(f"Received ping from {data['player']}, ee")
#     send({ "response": "hello" }, json=True)

def update_tile(game_id, tile):
    del tile["player_id"]
    del tile["game_id"]
    socketio.emit(f"{game_id}/update_tile", tile)