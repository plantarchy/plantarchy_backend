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
            """
            CREATE TABLE IF NOT EXISTS game (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                passcode VARCHAR(8),
                tileset VARCHAR(400),
                ownerset TEXT,
                state INTEGER
            )
            """
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS player (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), name VARCHAR(80), game_id UUID, CONSTRAINT fk_game FOREIGN KEY(game_id) REFERENCES game(id) ON DELETE CASCADE)"
        )
    db_conn.commit()
    print("Created tables")

def create_game(gameloop):
    with db_conn.cursor() as cur:
        tileset = []
        for row in gameloop.tiles:
            for tile in row:
                tileset.append(tile.crop)
        cur.execute(f"""
            INSERT INTO game(id, passcode, tileset, state) VALUES
            ('{gameloop.game_uuid}', '{gameloop.passcode}', '{gameloop.tileset}', 0)
        """)
    db_conn.commit()

def get_games():
    with db_conn.cursor() as cur:
        cur.execute(f"SELECT * FROM game") 
        return cur.fetchall()

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

def update_tileset(gameloop):
    with db_conn.cursor() as cur:
        tileset = []
        for row in gameloop.tiles:
            for tile in row:
                tileset.append(tile.crop)
        cur.execute(f"""
            UPDATE game SET tileset=%s WHERE id=%s
            ('{tileset}', '{gameloop.game_uuid}')
        """)
    db_conn.commit()