from datetime import date, timedelta
from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect
from typing import Any
from warnings import warn

from httpx import Response, get
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random


class StrandsGameData(BaseModel):
    board: list[tuple[str, int]]
    clue: str


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_data(*, date_str: str) -> str | None:
    response: Response = get(f"https://www.nytimes.com/svc/strands/v2/{date_str}.json")

    if response.status_code == 200:
        doc: dict[str, Any] = response.json()
        board: list[str] = doc["startingBoard"]

        assert len(board) == 8
        for row in board:
            assert len(row) == 6

        vis: list[list[bool]] = [[False for _ in range(6)] for _ in range(8)]
        dir: list[list[int]] = [[8 for _ in range(6)] for _ in range(8)]

        dir_map: dict[tuple[int, int], int] = {
            coord: index
            for index, coord in enumerate(
                ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1))
            )
        }

        def parse(*, coords: list[list[int]], is_spangram: bool) -> None:
            for i in range(len(coords)):
                cx: int
                cy: int
                cx, cy = coords[i]
                assert not vis[cx][cy]
                vis[cx][cy] = True

                if i < len(coords) - 1:
                    nx: int
                    ny: int
                    nx, ny = coords[i + 1]
                    dir[cx][cy] = dir_map[nx - cx, ny - cy]
                elif is_spangram:
                    dir[cx][cy] = 9

        parse(coords=doc["spangramCoords"], is_spangram=True)
        for coords in doc["themeCoords"].values():
            parse(coords=coords, is_spangram=False)

        assert all(all(row) for row in vis)

        return StrandsGameData(
            board=[(board[x][y], dir[x][y]) for x in range(8) for y in range(6)], clue=doc["clue"]
        ).model_dump_json()
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
                cur.execute("CREATE TABLE game(game_id, board)")

        start_date: date = date(2024, 3, 4)
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
            print(date_str)

            try:
                data_str: str | None = get_data(date_str=date_str)
            except Exception as e:
                warn(f"{date_str}: {repr(e)}")
                game_id += 1
                continue

            if data_str is None:
                print("break at", game_id, date_str)
                break

            with con:
                cur.execute("INSERT INTO game VALUES(?, ?)", (game_id, data_str))

            game_id += 1
    finally:
        con.close()


if __name__ == "__main__":
    main()
