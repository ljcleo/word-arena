from collections.abc import Callable, Iterable
from pathlib import Path
from random import Random
from typing import Any, override

from pydantic import BaseModel

from ....common.utils import get_db_cursor


class WordleMetaConfig(BaseModel):
    data_file: Path

    @override
    def model_post_init(self, context: Any) -> None:
        with get_db_cursor(data_file=self.data_file) as cur:
            self._word_pool: dict[int, str] = dict(cur.execute("SELECT word_id, word FROM word"))
            self._game_pool: dict[int, int] = dict(cur.execute("SELECT game_id, word_id FROM game"))

    @property
    def word_pool(self) -> dict[int, str]:
        return dict(self._word_pool)

    def select_game_ids(self, *, selector: Callable[[int], Iterable[int]]) -> list[int]:
        return list(map(self._game_pool.__getitem__, selector(len(self._game_pool))))

    def random_game_ids(self, *, count: int, rng: Random) -> list[int]:
        return rng.sample(list(self._game_pool.values()), k=count)


class WordleMutableMetaConfig(BaseModel):
    max_guesses: int
    num_targets: int


class WordleConfig(BaseModel):
    max_guesses: int
    game_ids: list[int]
