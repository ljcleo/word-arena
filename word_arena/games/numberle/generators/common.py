from collections.abc import Callable, Iterable
from pathlib import Path
from random import Random
from typing import Any, override

from pydantic import BaseModel

from ....common.utils import get_db_cursor


class NumberleMetaConfig(BaseModel):
    data_file: Path

    @override
    def model_post_init(self, context: Any) -> None:
        with get_db_cursor(data_file=self.data_file) as cur:
            self._eq_pool: dict[int, str] = dict(cur.execute("SELECT eq_id, eq FROM eq"))

            self._game_pool: dict[int, dict[int, int]] = {
                eq_length: dict(cur.execute(f"SELECT game_id, eq_id FROM game_{eq_length}"))
                for (eq_length,) in cur.execute(
                    "SELECT CAST(SUBSTR(name, 6) AS INTEGER) AS eq_length FROM sqlite_master "
                    "WHERE name LIKE 'game\\__%' ESCAPE '\\' ORDER BY eq_length"
                ).fetchall()
            }

    @property
    def eq_list(self) -> list[str]:
        return [self._eq_pool[i] for i in range(len(self._eq_pool))]

    @property
    def eq_length_pool(self) -> list[int]:
        return sorted(self._game_pool.keys())

    def select_game_ids(
        self, *, eq_length: int, selector: Callable[[int], Iterable[int]]
    ) -> list[int]:
        game_pool: dict[int, int] = self._game_pool[eq_length]
        return list(map(game_pool.__getitem__, selector(len(game_pool))))

    def random_game_ids(self, *, eq_length: int, rng: Random, count: int) -> list[int]:
        return rng.sample(list(self._game_pool[eq_length].values()), k=count)


class NumberleMutableMetaConfig(BaseModel):
    eq_length: int
    max_guesses: int
    num_targets: int


class NumberleConfig(BaseModel):
    eq_length: int
    max_guesses: int
    game_ids: list[int]
