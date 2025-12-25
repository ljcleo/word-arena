from collections.abc import Iterable, Iterator
from logging import WARNING, getLogger
from sqlite3 import Connection, Cursor, connect

from httpx import Response, get
from tenacity import before_sleep_log, retry, wait_random


def clear_or_create_table(
    *, con: Connection, cur: Cursor, table_name: str, fields: Iterable[str]
) -> None:
    with con:
        is_table_exist: bool = bool(
            cur.execute("SELECT 1 FROM sqlite_master WHERE name = ?", (table_name,)).fetchone()
        )

    with con:
        if not is_table_exist:
            cur.execute(f"CREATE TABLE {table_name}({', '.join(fields)})")
        else:
            cur.execute(f"DELETE FROM {table_name}")


@retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
def get_equations() -> Iterator[tuple[int, list[str]]]:
    response: Response = get("https://numberle.wordleday.org/files/equations.json?v1.81")

    if response.status_code == 200:
        yield from response.json().items()
    else:
        raise RuntimeError(response.status_code, response.reason_phrase, response.text)


def main() -> None:
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()

    try:
        clear_or_create_table(con=con, cur=cur, table_name="eq", fields=("eq_id", "eq"))
        n_eq: int = 0

        for eq_length, eqs in get_equations():
            game_table: str = f"game_{eq_length}"

            clear_or_create_table(
                con=con, cur=cur, table_name=game_table, fields=("game_id", "eq_id")
            )

            with con:
                cur.executemany(
                    "INSERT INTO eq VALUES(?, ?)", ((n_eq + i, eq) for i, eq in enumerate(eqs))
                )

                cur.executemany(
                    f"INSERT INTO {game_table} VALUES(?, ?)",
                    ((i, n_eq + i) for i in range(len(eqs))),
                )

            n_eq += len(eqs)
    finally:
        con.close()


if __name__ == "__main__":
    main()
