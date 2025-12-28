from pathlib import Path
from sqlite3 import Connection, Cursor, connect

from pydantic import BaseModel


def get_connections_game_count(*, data_file: Path) -> int:
    con: Connection = connect(data_file)
    cur: Cursor = con.cursor()

    try:
        with con:
            return cur.execute("SELECT COUNT(*) FROM game").fetchone()[0]
    finally:
        con.close()


class ConnectionsConfig(BaseModel):
    max_guesses: int
    game_id: int
