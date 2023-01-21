import random
import string
import psycopg
from psycopg.errors import SerializationFailure, Error
from psycopg.rows import dict_row

password = open("password.txt").read().strip()
db_uri = f"postgresql://vincent:{password}@bumpy-hermit-6946.5xj.cockroachlabs.cloud:26257/plantarchy-devdb?sslmode=verify-full"
print(db_uri)

db_conn = psycopg.connect(db_uri,
                       application_name="$ plantarchy_backend",
                       row_factory=dict_row)

def create_tables():
    print("Creating tables...")
    with db_conn.cursor() as cur:
        # DELETE EXISTING TABLES (FOR TESTING ONLY)
        cur.execute("DROP TABLE IF EXISTS tile")
        cur.execute("DROP TABLE IF EXISTS player")
        cur.execute("DROP TABLE IF EXISTS game")

        cur.execute(
            "CREATE TABLE IF NOT EXISTS game (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), passcode VARCHAR(8), state INTEGER)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS player (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name VARCHAR(80), game_id UUID, CONSTRAINT fk_game FOREIGN KEY(game_id) REFERENCES game(id) ON DELETE CASCADE)"
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tile
                (id SERIAL PRIMARY KEY,
                 game_id UUID,
                 player_id UUID,
                 crop INTEGER,
                 x_coord INTEGER, y_coord INTEGER,
                 CONSTRAINT fk_game FOREIGN KEY(game_id) REFERENCES game(id) ON DELETE CASCADE,
                 CONSTRAINT fk_player FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE)
            """
        )
        create_game()
    db_conn.commit()
    print("Created tables")

def create_game():
    with db_conn.cursor() as cur:
        # game_code = "".join(random.choice(string.ascii_uppercase) for a in range(8))
        game_code = "ABCDABCD"
        cur.execute(f"INSERT INTO game(passcode, state) VALUES ('{game_code}', 0)")
        game = get_game(game_code)
        qs = "INSERT INTO tile(x_coord, y_coord, crop, game_id) VALUES "
        for i, r in enumerate(range(20)):
            if i > 0: qs += ", "
            for j,c in enumerate(range(20)):
                if j > 0: qs += ", "
                qs += f"({c}, {r}, 0, '{game['id']}')"
        cur.execute(qs)
    db_conn.commit()

def get_games():
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM game")
        return cur.fetchall()

def get_game_by_uuid(uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM game WHERE id=%s LIMIT 1", (uuid,))
        return cur.fetchone()

def get_game(passcode):
    print("agawg", passcode)
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM game WHERE passcode=%s LIMIT 1", (passcode,))
        return cur.fetchone()

def get_user(player_name, game_uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM player WHERE name=%s AND game_id=%s LIMIT 1", (player_name, game_uuid))
        return cur.fetchone()

def get_user_by_uuid(player_uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM player WHERE id=%s LIMIT 1", (player_uuid,))
        return cur.fetchone()

def create_user(player_name, game_uuid):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO player(name, game_id) VALUES (%s, %s)", (player_name, game_uuid))
    db_conn.commit()

def get_tiles(game_uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM tile WHERE game_id=%s", (game_uuid,))
        return cur.fetchall()

def get_tile(x, y, game_uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM tile WHERE x_coord=%s AND y_coord=%s AND game_id=%s LIMIT 1", (x, y, game_uuid,))
        return cur.fetchone()

def get_tile_by_uuid(tile_uuid):
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM tile WHERE id=%s LIMIT 1", (tile_uuid,))
        return cur.fetchone()

def set_tile(crop, player_uuid, tile_id):
    with db_conn.cursor() as cur:
        cur.execute("UPDATE tile SET crop=%s, player_id=%s WHERE id=%s LIMIT 1", (crop, player_uuid, tile_id))
    db_conn.commit()