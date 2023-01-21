import random
import string
import uuid
import time
from dataclasses import dataclass
import threading
from datetime import datetime, timedelta

TICKSPEED = 1 / 20
GRIDSIZE = 20

g_gameloops = {}

@dataclass
class Plant:
    owner: str
    crop: int
    x: int
    y: int

class AlreadyOwnedError(Exception):
    """
    Already owned.
    """
    pass

class Gameloop(threading.Thread):
    def __init__(self, game_uuid, passcode, tileset = "", ownerset = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_uuid = game_uuid
        self.passcode = passcode
        self.last_tick = datetime.now()
        self.tiles = []
        self.players = {}
        for r in range(GRIDSIZE):
            self.tiles.append([])
            for c in range(GRIDSIZE):
                self.tiles[r].append(Plant("", 0, c, r))
        ownerlist = ownerset.split(",")
        if tileset != "":
            for r in range(GRIDSIZE):
                for c in range(GRIDSIZE):
                    self.tiles[r][c].crop = tileset[r * GRIDSIZE + c]
                    self.tiles[r][c].owner = ownerlist[r * GRIDSIZE + c]

    def set_tile(self, x, y, crop, player_uuid):
        if self.tiles[y][x].owner != "":
            raise AlreadyOwnedError
        self.tiles[y][x].crop = crop
        self.tiles[y][x].owner = player_uuid

    def add_user(self, username):
        id = str(uuid.uuid4())
        self.players[id] = username
        return id

    def run(self):
        while True:
            self.next_tick = datetime.now() + timedelta(seconds=TICKSPEED)
            # print(self.next_tick)
            time.sleep((self.next_tick - datetime.now()).microseconds / 1e6)

    def to_json(self):
        return {
            "id": self.game_uuid,
            "passcode": self.passcode,
        }

    def to_tuple(self):
        tileset = ""
        ownerset = ""
        for r in range(GRIDSIZE):
            for c in range(GRIDSIZE):
                tileset += self.tiles[r][c].crop
                ownerset += ("," if c > 0 else "") + self.tiles[r][c].owner

        return (
            self.game_uuid,
            self.passcode,
            tileset,
            ownerset
        )

    def tileset(self):
        _tileset = []
        for r in range(GRIDSIZE):
            for c in range(GRIDSIZE):
                _tileset.append({
                    "player_uuid": self.tiles[r][c].owner,
                    "crop": self.tiles[r][c].crop,
                    "x": c,
                    "y": r,
                })
        return _tileset

def create_game(game_code):
    global g_gameloops
    if game_code == "":
        game_code = "".join(random.choice(string.ascii_uppercase) for i in range(8))
    id = str(uuid.uuid4())
    g_gameloops[id] = Gameloop(id, game_code)
    print("gameloop", g_gameloops)
    return g_gameloops[id]