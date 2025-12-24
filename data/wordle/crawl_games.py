from datetime import date, timedelta
from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect
from warnings import warn

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_word(*, date_str: str) -> str | None:
    response: Response = get(f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json")

    if response.status_code == 200:
        return response.json()["solution"]
    elif response.status_code == 404:
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
                cur.execute("CREATE TABLE game(game_id, word_id)")

        start_date: date = date(2021, 6, 19)
        game_id: int = 0

        while True:
            with con:
                has_game: bool = bool(
                    cur.execute("SELECT 1 FROM game WHERE game_id = ?", (game_id,)).fetchone()
                )

            if has_game:
                game_id += 1
                continue

            date_str: str = (start_date + timedelta(days=game_id)).strftime("%Y-%m-%d")
            print(game_id, date_str)

            try:
                word: str | None = get_word(date_str=date_str)
            except Exception as e:
                warn(f"{date_str}: {repr(e)}")
                game_id += 1
                continue

            if word is None:
                print("break at", game_id, date_str)
                break

            with con:
                word_info: tuple[int] | None = cur.execute(
                    "SELECT word_id FROM word WHERE word = ?", (word,)
                ).fetchone()

            if word_info is None:
                warn(f"{date_str}: word {word} not in word database")
                game_id += 1
                continue

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, word_info[0]))

            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()
