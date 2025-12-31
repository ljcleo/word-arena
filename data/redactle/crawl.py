from logging import WARNING, getLogger
from re import IGNORECASE, findall
from sqlite3 import Connection, Cursor, connect
from typing import Any
from warnings import warn

from httpx import Response, get
from markdownify import markdownify
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random


class RedactleGameData(BaseModel):
    article: list[tuple[str, str | None]]
    lemma_map: dict[str, str]


@retry(wait=wait_random(max=10), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_data(*, game_id: int) -> str | bool:
    response: Response = get(f"https://redactle.net/api/article/en/daily/{game_id}")

    if response.status_code == 200:
        doc: dict[str, Any] = response.json()

        lemma_map: dict[str, str] = {
            word.lower(): lemma[0].lower()
            for word, lemma in doc["lemmas"]
            if len(lemma) == 1 and lemma[0] is not None
        }

        return RedactleGameData(
            article=[
                (m1 or m2, None if m1 == "" else lemma_map.get(m1.lower(), m1.lower()))
                for m1, m2 in findall(
                    "([\u00bf-\u1fff\u2c00-\ud7ff\u2654-\u265f\\w]+)|"
                    "([^\u00bf-\u1fff\u2c00-\ud7ff\u2654-\u265f\\w]+)",
                    markdownify(doc["article"]),
                    flags=IGNORECASE,
                )
            ],
            lemma_map=lemma_map,
        ).model_dump_json()
    elif response.status_code == 404:
        return response.json()["message"] == "Redactle ID out of range"
    elif response.status_code == 500:
        return False
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
                cur.execute("CREATE TABLE game(game_id, data)")

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
                data_str: str | bool = get_data(game_id=game_id)
            except Exception as e:
                warn(f"{game_id}: {repr(e)}")
                game_id += 1
                continue

            if isinstance(data_str, bool):
                if data_str:
                    print("break at", game_id)
                    break
                else:
                    print("skip", game_id)
                    game_id += 1
                    continue

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, data_str))

            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()
