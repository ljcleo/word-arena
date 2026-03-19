from collections.abc import Callable
from datetime import date
from random import Random
from typing import Any, override

from pydantic import BaseModel


class ContextoMetaConfig(BaseModel):
    base_url: str

    @override
    def model_post_init(self, context: Any) -> None:
        self._game_pool: list[int] = list(range((date.today() - date(2022, 9, 18)).days + 1))

    def select_game_id(self, *, selector: Callable[[int], int]) -> int:
        return self._game_pool[selector(len(self._game_pool))]

    def random_game_id(self, *, rng: Random) -> int:
        return rng.choice(self._game_pool)
