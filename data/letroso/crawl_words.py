from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_words() -> list[str]:
    response: Response = get("https://letroso.com/static/js/577.7e0847a6.chunk.js")

    if response.status_code == 200:
        return sorted(eval(f"{{{response.text.partition("parse('[")[2].partition(']')[0]}}}"))
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        words: list[str] = get_words()

        with con:
            is_table_exist: bool = bool(
                cur.execute("SELECT 1 FROM sqlite_master WHERE name = 'word'").fetchone()
            )

        games: tuple[tuple[int, int], ...] | None = None

        if is_table_exist:
            with con:
                is_game_table_exist: bool = bool(
                    cur.execute("SELECT 1 FROM sqlite_master WHERE name = 'game'").fetchone()
                )

            if is_game_table_exist:
                word_map: dict[str, int] = {word: index for index, word in enumerate(words)}

                with con:
                    games = tuple(
                        (game_id, word_map[word])
                        for game_id, word in cur.execute(
                            "SELECT game.game_id, word.word FROM game "
                            "INNER JOIN word ON game.word_id = word.word_id"
                        )
                    )

        with con:
            if is_table_exist:
                cur.execute("DELETE FROM word")
                if games is not None:
                    cur.execute("DELETE FROM game")
            else:
                cur.execute("CREATE TABLE word(word_id, word)")

            cur.executemany("INSERT INTO word VALUES(?, ?)", tuple(enumerate(words)))
            if games is not None:
                cur.executemany("INSERT INTO game VALUES(?, ?)", games)
    finally:
        con.close()


if __name__ == "__main__":
    main()
