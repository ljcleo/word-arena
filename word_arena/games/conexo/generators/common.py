from collections.abc import Callable
from pathlib import Path
from random import Random
from typing import Any, override

from pydantic import BaseModel

from ....common.utils import get_db_cursor


class ConexoMetaConfig(BaseModel):
    data_file: Path

    @override
    def model_post_init(self, context: Any) -> None:
        with get_db_cursor(data_file=self.data_file) as cur:
            self._game_pool: list[int] = [
                row[0] for row in cur.execute("SELECT game_id FROM game ORDER BY game_id")
            ]

    def select_game_id(self, *, selector: Callable[[int], int]) -> int:
        return self._game_pool[selector(len(self._game_pool))]

    def random_game_id(self, *, rng: Random) -> int:
        return rng.choice(self._game_pool)


class ConexoConfig(BaseModel):
    max_guesses: int
    game_id: int
