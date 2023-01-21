import time
import threading
from datetime import datetime, timedelta
from .db import get_game, get_tiles, set_tile

TICKSPEED = 1 / 20

class Gameloop(threading.Thread):
    def __init__(self, game_uuid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_uuid = game_uuid
        self.last_tick = datetime.now()
        self.tiles = {}
        for tile in get_tiles(self.game_uuid):
            self.tiles[(tile["x_coord"], tile["y_coord"])] = tile

    def set_tile(self, tile):
        self.tiles[(tile["x_coord"], tile["y_coord"])] = tile

    def run(self):
        while True:
            self.next_tick = datetime.now() + timedelta(seconds=TICKSPEED)
            # print(self.next_tick)
            time.sleep((self.next_tick - datetime.now()).microseconds / 1e6)