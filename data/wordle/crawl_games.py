from datetime import date, timedelta
from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect
from warnings import warn

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_word(*, date_str: str) -> str:
    response: Response = get(f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json")

    if response.status_code == 200:
        return response.json()["solution"]
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        with con:
            word_map: dict[str, int] = {
                word: index
                for word, index in cur.execute("SELECT word_id, word FROM word").fetchall()
            }

        with con:
            is_table_exist: bool = bool(
                cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE name = 'game'").fetchone()[0]
            )

        if not is_table_exist:
            with con:
                cur.execute("CREATE TABLE game(game_id, word_id)")

        target_date: date = date(2021, 6, 19)
        game_id: int = 0

        while target_date <= date.today():
            with con:
                has_game: bool = bool(
                    cur.execute(
                        "SELECT COUNT(*) FROM game WHERE game_id = ?", (game_id,)
                    ).fetchone()[0]
                )

            if has_game:
                target_date += timedelta(days=1)
                game_id += 1
                continue

            date_str: str = target_date.strftime("%Y-%m-%d")
            print(date_str)

            try:
                word_id: int = word_map[get_word(date_str=date_str)]
            except Exception as e:
                warn(f"{date_str}: {repr(e)}")
                target_date += timedelta(days=1)
                game_id += 1
                continue

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, word_id))

            target_date += timedelta(days=1)
            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()
