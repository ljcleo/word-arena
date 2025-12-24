from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_words() -> set[str]:
    response: Response = get("https://www.nytimes.com/games-assets/v2/7471.ca837e2d94ae3f5e505b.js")

    if response.status_code == 200:
        return eval(f"{{{response.text.partition('const o=[')[2].partition(']')[0]}}}")
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        with con:
            is_table_exist: bool = bool(
                cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE name = 'word'").fetchone()[0]
            )

        with con:
            if is_table_exist:
                cur.execute("TRUNCATE TABLE word")
            else:
                cur.execute("CREATE TABLE word(word_id, word)")

        with con:
            cur.executemany("INSERT INTO word VALUES(?, ?)", tuple(enumerate(sorted(get_words()))))
    finally:
        con.close()


if __name__ == "__main__":
    main()
