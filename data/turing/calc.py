from collections.abc import Iterable, Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from itertools import combinations, product
from json import dumps, load
from multiprocessing import Manager
from queue import Queue
from sqlite3 import Connection, Cursor, connect

type Code = tuple[int, int, int]
type CodeSet = set[Code]
type CardIDs = tuple[int, ...]
type Keys = tuple[int, ...]
type KeyCodePair = tuple[Keys, Code]
type Output = tuple[int, int, int, int]


def univ() -> CodeSet:
    return set(product(range(1, 6), range(1, 6), range(1, 6)))


def verify(*, card_code_sets: list[list[CodeSet]], card_ids: CardIDs) -> Iterator[KeyCodePair]:
    def check(*, keys: Keys) -> bool:
        for i in range(len(card_ids)):
            code_set: CodeSet = univ()

            for j in range(len(card_ids)):
                if j != i:
                    code_set &= card_code_sets[card_ids[j]][keys[j]]
                    if len(code_set) < 2:
                        return False

        return True

    def dfs(*, keys: Keys, code_set: CodeSet) -> Iterator[KeyCodePair]:
        if len(keys) == len(card_ids):
            if len(code_set) == 1 and check(keys=keys):
                yield keys, list(code_set)[0]
        elif len(code_set) > 1:
            for key, card_code_set in enumerate(card_code_sets[card_ids[len(keys)]]):
                new_code_set: CodeSet = code_set & card_code_set
                if len(new_code_set) > 0:
                    yield from dfs(keys=(*keys, key), code_set=new_code_set)

    yield from dfs(keys=(), code_set=univ())


def pack(*, data: Iterable[int], base: int) -> int:
    result: int = 0

    for value in data:
        assert 0 <= value < base
        result = result * base + value

    return result


def work(
    *,
    card_pool: list[list[str]],
    input_queue: Queue[tuple[int, CardIDs] | None],
    output_queue: Queue[Output | None],
):
    card_code_sets: list[list[CodeSet]] = [
        [{(x, y, z) for x, y, z in univ() if eval(expr)} for expr in card] for card in card_pool
    ]

    try:
        while (data := input_queue.get(timeout=30)) is not None:
            work_id: int
            card_ids: CardIDs
            work_id, card_ids = data

            if (work_id + 1) % 100000 == 0:
                print("WORK", work_id + 1)

            try:
                for keys, code in verify(card_code_sets=card_code_sets, card_ids=card_ids):
                    output_queue.put(
                        (
                            len(card_ids),
                            pack(data=card_ids, base=64),
                            pack(data=keys, base=16),
                            pack(data=code, base=10),
                        )
                    )

            except Exception as e:
                print(f"WORK {work_id} ERROR:", repr(e))
                raise
    except Exception as e:
        print("WORK ERROR:", repr(e))


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


def write_db(*, card_pool: list[list[str]], output_queue: Queue[Output | None]):
    con: Connection = connect("./games.db")
    cur: Cursor = con.cursor()
    write_cnt: int = 0

    try:
        clear_or_create_table(con=con, cur=cur, table_name="card", fields=("card_id", "card"))

        with con:
            cur.executemany(
                "INSERT INTO card VALUES(?, ?)",
                tuple(
                    enumerate(
                        dumps(card, ensure_ascii=False, separators=(",", ":")) for card in card_pool
                    )
                ),
            )

        table_sz: dict[str, int] = {}
        table_buf: dict[str, list[Output]] = {}

        while (data := output_queue.get(timeout=30)) is not None:
            n_cards: int
            card_id: int
            keys: int
            code: int
            n_cards, card_id, keys, code = data
            table_name: str = f"game_{n_cards}"

            if table_name not in table_sz:
                clear_or_create_table(
                    con=con,
                    cur=cur,
                    table_name=table_name,
                    fields=("game_id", "card_id", "key", "code"),
                )

                table_sz[table_name] = 0
                table_buf[table_name] = []

            table_buf[table_name].append((table_sz[table_name], card_id, keys, code))
            table_sz[table_name] += 1
            write_cnt += 1

            if len(table_buf[table_name]) >= 65536:
                with con:
                    cur.executemany(
                        f"INSERT INTO {table_name} VALUES(?, ?, ?, ?)", tuple(table_buf[table_name])
                    )

                table_buf[table_name].clear()

            if write_cnt % 100000 == 0:
                print("WRITE", write_cnt)

        for table_name, buf in table_buf.items():
            if len(buf) > 0:
                with con:
                    cur.executemany(
                        f"INSERT INTO {table_name} VALUES(?, ?, ?, ?)", tuple(table_buf[table_name])
                    )

                table_buf[table_name].clear()
    except Exception as e:
        print("WRITE ERROR:", repr(e))
    finally:
        print("TOTAL WRITE", write_cnt)
        con.close()


def main():
    min_cards: int = int(input("Min cards: "))
    max_cards: int = int(input("Max cards: "))
    max_workers: int = int(input("Max workers: "))

    with open("./cards.json", encoding="utf8") as f:
        card_pool: list[list[str]] = load(f)

    with Manager() as man:
        input_queue: Queue[tuple[int, CardIDs] | None] = man.Queue(maxsize=32768)
        output_queue: Queue[Output | None] = man.Queue(maxsize=32768)

        with ProcessPoolExecutor(max_workers=max_workers + 1) as pool:
            writer_future: Future[None] = pool.submit(
                write_db, card_pool=card_pool, output_queue=output_queue
            )

            worker_futures: list[Future[None]] = [
                pool.submit(
                    work, card_pool=card_pool, input_queue=input_queue, output_queue=output_queue
                )
                for _ in range(max_workers)
            ]

            work_id = 0

            for n_cards in range(min_cards, max_cards + 1):
                for work_id, card_ids in enumerate(combinations(range(len(card_pool)), n_cards)):
                    input_queue.put((work_id, card_ids), timeout=60)

            for _ in range(max_workers):
                input_queue.put(None, timeout=60)
            for future in worker_futures:
                future.result()

            print("TOTAL WORK", work_id + 1)
            output_queue.put(None, timeout=60)
            writer_future.result()


if __name__ == "__main__":
    main()
