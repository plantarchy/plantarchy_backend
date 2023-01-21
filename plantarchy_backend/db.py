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
        cur.execute("DROP TABLE IF EXISTS tiles")
        cur.execute("DROP TABLE IF EXISTS player")
        cur.execute("DROP TABLE IF EXISTS game")

        cur.execute(
            "CREATE TABLE IF NOT EXISTS game (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), passcode VARCHAR(8), state INTEGER)"
        )
        cur.execute("INSERT INTO game(passcode, state) VALUES ('ABCDABCD', 0)")
        cur.execute("INSERT INTO game(passcode, state) VALUES ('ABCDABCD', 0)")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS player (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), game_id UUID, CONSTRAINT fk_game FOREIGN KEY(game_id) REFERENCES game(id) ON DELETE CASCADE)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS tiles (id SERIAL PRIMARY KEY, player_id UUID, crop VARCHAR(32), x_coordinate INTEGER, y_coordinate INTEGER, CONSTRAINT fk_player FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE)"
        )
    db_conn.commit()
    print("Created tables")

def get_games():
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM game")
        return cur.fetchall()
