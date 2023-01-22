import random
import string
import uuid
import time
from math import *
from dataclasses import dataclass
import threading
from .events import update_tile
from .globals import g_gameloops, g_player_gamemap, g_player_timeout
from datetime import datetime, timedelta

TICKSPEED = 1 / 1
GRIDSIZE = 35

class Plant:
    def __init__(self, game: 'Gameloop', owner, crop, x, y, age = 0):
        self.game = game
        self.owner = owner
        self.crop = crop
        self.x = x
        self.y = y
        self.age = age

    def evolve(self, fertilize=False):

        if 1 < self.crop <= 4:
            self.age += 1
            death_bound = floor(80/(abs(self.game.count_neighbors(self.x, self.y) - 4) + 1))
            #(self.game.count_enemies(self, self.x, self.y) + 1)x
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
                threshold = 14 if fertilize else 29
                if random.randint(0, threshold) == 0:
                    self.crop = 2
                    self.game.trigger_neighbors(self.x, self.y, self.owner)
            else:
                # print("Prune", self.x, self.y)
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
        self.land = 0
        self.next_seed_in = 3

    def add_seed(self):
        self.next_seed_in -= 1
        if self.next_seed_in == 0:
            if self.seeds < 200:
                self.seeds += 1
            self.next_seed_in = 3

    def to_json(self):
        return {
            "id": self.player_uuid,
            "game_uuid": self.game_uuid,
            "player_name": self.player_name,
            "berries": self.berries,
            "seeds": self.seeds,
            "land": self.land,
        }

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

class NoBerriesError(Exception):
    """
    No berries
    """
    pass

class Gameloop(threading.Thread):
    def __init__(self, game_uuid, passcode, tileset = "", ownerset = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_uuid = game_uuid
        self.passcode = passcode
        self.last_tick = datetime.now()
        self.fertilize_ticks = {}
        self.tiles = []
        self.players = {}
        self.player_timeouts = {}
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
        if (self.tiles[y][x].owner not in {player_uuid, ""}) or (self.tiles[y][x].crop != 1 and self.tiles[y][x].owner != ""):
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
        self.player_timeouts[id] = 2
        g_player_gamemap[id] = self
        return id

    def run(self):
        while True:
            self.next_tick = datetime.now() + timedelta(seconds=TICKSPEED)
            # print("Next tick at", self.next_tick)
            self.evolve()
            for id, player in self.players.items():
                player.add_seed()
            to_remove = []
            for player, v in self.player_timeouts.items():
                self.player_timeouts[player] -= 1
                if self.player_timeouts[player] <= 0:
                    self.clear(player)
                    to_remove.append(player)
            for player in to_remove:
                try:
                    del self.player_timeouts[player]
                    del self.players[player]
                except KeyError:
                    pass

            print(self.players, self.player_timeouts)

            for player, v in self.fertilize_ticks.items():
                if self.fertilize_ticks[player] > 0:
                    self.fertilize_ticks[player] -= 1
            time.sleep((self.next_tick - datetime.now()).microseconds / 1e6)

    def to_json(self):
        return {
            "id": self.game_uuid,
            "passcode": self.passcode,
        }

    def clear(self, player_uuid):
        for r in range(GRIDSIZE):
            for c in range(GRIDSIZE):
                if self.tiles[r][c].owner == player_uuid:
                    self.tiles[r][c].crop = 0
                    self.tiles[r][c].owner = ""
                    update_tile(self.game_uuid, self.tiles[r][c])

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
        counts = {}
        for r in range(GRIDSIZE):
            for c in range(GRIDSIZE):
                old_evo = self.tiles[r][c].crop
                self.tiles[r][c].evolve(self.fertilize_ticks.get(self.tiles[r][c].owner, 0) > 0)
                if self.tiles[r][c].crop != old_evo:
                    # print("Tile at", r, c, "changed from", old_evo, "to", self.tiles[r][c].crop)
                    update_tile(self.game_uuid, self.tiles[r][c])
                if self.tiles[r][c].crop >= 2:
                    if self.tiles[r][c].owner not in counts:
                        counts[self.tiles[r][c].owner] = 0
                    counts[self.tiles[r][c].owner] += 1
        for id,count in counts.items():
            self.players[id].land = count

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
    
    def count_enemies(self, owner, x, y):
        count = 0
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        for dir in dirs:
            if not (0 <= x + dir[0] < GRIDSIZE and 0 <= y + dir[1] < GRIDSIZE):
                continue
            if self.tiles[y + dir[1]][x + dir[0]].crop > 1 and self.tiles[y + dir[1]][x + dir[0]].owner != owner:
                count += 1
        return count

    def berry_bomb(self, player_uuid, x, y):
        if self.players[player_uuid].berries >= 15:
            self.players[player_uuid].berries -= 15
        else:
            raise NoBerriesError

        count = 0
        # dirs = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        for r in range(-2, 3):
            for c in range(-2, 3):
                if not (0 <= x + c < GRIDSIZE and 0 <= y + r < GRIDSIZE):
                    continue
                self.tiles[y + r][x + c].crop = 0
                update_tile(self.game_uuid, self.tiles[y + r][x + c])
        
    def fertilize(self, player_uuid):
        if self.players[player_uuid].berries >= 30:
            self.players[player_uuid].berries -= 30
            self.fertilize_ticks[player_uuid] = 10
        else:
            raise NoBerriesError

    def extract(self, player_uuid):
        if self.players[player_uuid].berries >= 10:
            self.players[player_uuid].berries -= 10
            self.players[player_uuid].seeds += 5
        else:
            raise NoBerriesError

def create_game(game_code):
    global g_gameloops
    if game_code == "":
        game_code = "".join(random.choice(string.ascii_uppercase) for i in range(8))
    id = str(uuid.uuid4())
    g_gameloops[id] = Gameloop(id, game_code)
    return g_gameloops[id]