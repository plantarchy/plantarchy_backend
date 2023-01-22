import random
import string
import uuid
import time
from math import *
from dataclasses import dataclass
import threading
from .events import update_tile
from datetime import datetime, timedelta

TICKSPEED = 1 / 1
GRIDSIZE = 35

g_gameloops = {}

class Plant:
    def __init__(self, game: 'Gameloop', owner, crop, x, y, age = 0):
        self.game = game
        self.owner = owner
        self.crop = crop
        self.x = x
        self.y = y
        self.age = age

    def evolve(self):

        if 1 < self.crop <= 4:
            self.age += 1
            death_bound = floor(80/(abs(self.game.count_neighbors(self.x, self.y) - 4) + 1))
            die = False
            if (self.age < death_bound - 1):
                die = random.randint(0, death_bound - self.age - 1) == 0
            else:
                die = True
            if die:
                if (self.game.count_neighbors(self.x, self.y) >= 1):
                    self.crop = 1
                else:
                    self.crop = 0

            if self.crop == 2:
                if self.age < 9:
                    if random.randint(0, 10 - self.age - 1) == 0:
                        self.crop = 3
                else:
                    self.crop = 3
            elif self.crop == 3:
                if random.randint(0, 19) == 19:
                    self.crop = 4
            elif self.crop == 4:
                if random.randint(0, 9) == 0:
                    self.crop = 3
        elif self.crop == 1:
            self.age = 0
            if (self.game.count_neighbors(self.x, self.y) >= 1):
                if random.randint(0, 29) == 0:
                    self.crop = 2
                    self.game.trigger_neighbors(self.x, self.y, self.owner)
            else:
                print("Prune", self.x, self.y)
                self.crop = 0
                self.owner = ""
        elif self.crop == 0:
            self.age = 0
            self.owner = ""

class Player:
    def __init__(self, player_name, player_uuid, game_uuid):
        self.player_name = player_name
        self.player_uuid = player_uuid
        self.game_uuid = game_uuid
        self.berries = 0
        self.seeds = 5
        self.next_seed_in = 3

    def add_seed(self):
        self.next_seed_in -= 1
        if self.next_seed_in == 0:
            self.seeds += 1
            self.next_seed_in = 3

class AlreadyOwnedError(Exception):
    """
    Already owned.
    """
    pass

class NoPlayerError(Exception):
    """
    Already owned.
    """
    pass

class NoSeedsError(Exception):
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
                self.tiles[r].append(Plant(self, "", 0, c, r))
        ownerlist = ownerset.split(",")
        if tileset != "":
            for r in range(GRIDSIZE):
                for c in range(GRIDSIZE):
                    self.tiles[r][c].crop = tileset[r * GRIDSIZE + c]
                    self.tiles[r][c].owner = ownerlist[r * GRIDSIZE + c]

    def set_tile(self, x, y, crop, player_uuid):
        if self.tiles[y][x].owner != "":
            raise AlreadyOwnedError
        if player_uuid not in self.players:
            raise NoPlayerError
        player = self.players[player_uuid]
        if player.seeds <= 0:
            raise NoSeedsError

        tile = self.tiles[y][x]
        if tile.crop < 2:
            tile.crop = crop
            tile.owner = player_uuid
            self.trigger_neighbors(tile.x, tile.y, tile.owner)
            player.seeds -= 1

    def add_user(self, username):
        id = str(uuid.uuid4())
        self.players[id] = Player(username, id, self.game_uuid)
        return id

    def run(self):
        while True:
            self.next_tick = datetime.now() + timedelta(seconds=TICKSPEED)
            print("Next tick at", self.next_tick)
            self.evolve()
            for id, player in self.players.items():
                player.add_seed()
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
                    "x_coord": c,
                    "y_coord": r,
                })
        return _tileset

    def evolve(self):
        for r in range(GRIDSIZE):
            for c in range(GRIDSIZE):
                old_evo = self.tiles[r][c].crop
                self.tiles[r][c].evolve()
                if self.tiles[r][c].crop != old_evo:
                    print("Tile at", r, c, "changed from", old_evo, "to", self.tiles[r][c].crop)
                    update_tile(self.game_uuid, self.tiles[r][c])

    def trigger_neighbors(self, x, y, owner):
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        for dir in dirs:
            if not (0 <= x + dir[0] < GRIDSIZE and 0 <= y + dir[1] < GRIDSIZE):
                continue
            tile = self.tiles[y + dir[1]][x + dir[0]]
            if tile.crop == 0 and (tile.owner == "" or tile.owner == owner):
                tile.crop = 1
                tile.owner = owner
                update_tile(self.game_uuid, tile)
            elif tile.crop == 1:
                tile.crop = 1
                tile.owner = owner
                update_tile(self.game_uuid, tile)

    def count_neighbors(self, x, y):
        count = 0
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        for dir in dirs:
            if not (0 <= x + dir[0] < GRIDSIZE and 0 <= y + dir[1] < GRIDSIZE):
                continue
            if self.tiles[y + dir[1]][x + dir[0]].crop > 1:
                count += 1
        return count

def create_game(game_code):
    global g_gameloops
    if game_code == "":
        game_code = "".join(random.choice(string.ascii_uppercase) for i in range(8))
    id = str(uuid.uuid4())
    g_gameloops[id] = Gameloop(id, game_code)
    return g_gameloops[id]