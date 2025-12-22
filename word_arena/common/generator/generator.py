from abc import ABC, abstractmethod
from collections.abc import Iterable
from random import Random

from ..game.base import BaseGame
from .provider import BaseGameProvider


class BaseGameGenerator[ST, CT, GT: BaseGame](BaseGameProvider[CT, GT], ABC):
    def __init__(self, *, setting_pool: Iterable[ST], seed: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self._setting_pool: list[ST] = list(setting_pool)
        self._rng: Random = Random(seed)

    def random_game(self) -> GT:
        return self.create_game(
            config=self.generate_config(setting=self._rng.choice(self._setting_pool), rng=self._rng)
        )

    @abstractmethod
    def generate_config(self, *, setting: ST, rng: Random) -> CT:
        raise NotImplementedError()
