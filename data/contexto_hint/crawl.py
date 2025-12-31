from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect
from warnings import warn

from httpx import Response, get
from pydantic import TypeAdapter
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_top(*, game_id: int) -> str | None:
    response: Response = get(f"https://api.contexto.me/machado/en/top/{game_id}")

    if response.status_code == 200:
        return TypeAdapter(list[str]).dump_json(response.json()["words"]).decode(encoding="utf8")
    elif response.status_code == 500:
        return None
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        with con:
            is_table_exist: bool = bool(
                cur.execute("SELECT 1 FROM sqlite_master WHERE name = 'game'").fetchone()
            )

        if not is_table_exist:
            with con:
                cur.execute("CREATE TABLE game(game_id, top_words)")

        game_id: int = 0

        while True:
            with con:
                has_game: bool = bool(
                    cur.execute("SELECT 1 FROM game WHERE game_id = ?", (game_id,)).fetchone()
                )

            if has_game:
                game_id += 1
                continue

            print(game_id)

            try:
                top_words: str | None = get_top(game_id=game_id)
            except Exception as e:
                warn(f"{game_id}: {repr(e)}")
                game_id += 1
                continue

            if top_words is None:
                print("break at", game_id)
                break

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, top_words))

            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()
