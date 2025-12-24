from abc import ABC, abstractmethod
from collections.abc import Iterable
from random import Random

from ..game.base import BaseGame
from .provider import BaseGameProvider


class BaseGameGenerator[MT, UT, CT, GT: BaseGame](BaseGameProvider[MT, CT, GT], ABC):
    def __init__(
        self, *, meta_config: MT, mutable_meta_config_pool: Iterable[UT], seed: int, **kwargs
    ) -> None:
        super().__init__(meta_config=meta_config, **kwargs)
        self._mutable_meta_config_pool: list[UT] = list(mutable_meta_config_pool)
        self._rng: Random = Random(seed)

    def random_game(self) -> GT:
        return self.create_game(
            meta_config=self.meta_config,
            config=self.generate_config(
                meta_config=self.meta_config,
                mutable_meta_config=self._rng.choice(self._mutable_meta_config_pool),
                rng=self._rng,
            ),
        )

    @abstractmethod
    def generate_config(self, *, meta_config: MT, mutable_meta_config: UT, rng: Random) -> CT:
        raise NotImplementedError()
