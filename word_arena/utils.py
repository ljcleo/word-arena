from collections.abc import Generator, Iterable
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from sqlite3 import Connection, Cursor, connect


@contextmanager
def get_db_cursor(*, data_file: Path) -> Generator[Cursor, None, None]:
    con: Connection = connect(data_file)
    cur: Cursor = con.cursor()

    try:
        with con:
            yield cur
    finally:
        con.close()


def create_seed(*, data: str | bytes) -> int:
    if isinstance(data, str):
        data = data.encode(encoding="utf8")

    return int(sha256(data).hexdigest(), base=16) & ((1 << 32) - 1)


def join_or_na(items: Iterable[str], /) -> str:
    result: str = ", ".join(items)
    return "N/A" if result == "" else result
