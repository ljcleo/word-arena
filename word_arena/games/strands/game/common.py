from collections.abc import Callable
from pathlib import Path
from random import Random
from typing import Any, override

from pydantic import BaseModel

from ....common.game.state import GameStateInterface
from ....utils import get_db_cursor
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo


class StrandsMetaConfig(BaseModel):
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


class StrandsConfig(BaseModel):
    data_file: Path
    max_turns: int
    game_id: int


class StrandsGameData(BaseModel):
    board: list[tuple[str, int]]
    clue: str


type StrandsGameStateInterface = GameStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult
]
