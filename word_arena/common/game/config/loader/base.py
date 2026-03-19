from abc import ABC, abstractmethod
from collections.abc import Iterable
from random import Random

from ..reader.base import BaseConfigReader


class BaseConfigLoader[MT, UT, CT](ABC):
    def __init__(
        self,
        *,
        meta_config: MT,
        mutable_meta_config_pool: Iterable[UT] | None,
        reader: BaseConfigReader[MT, CT],
    ) -> None:
        self._meta_config: MT = meta_config

        self._mutable_meta_config_pool: list[UT] = (
            [] if mutable_meta_config_pool is None else list(mutable_meta_config_pool)
        )

        self._reader: BaseConfigReader[MT, CT] = reader

    def load_config(self) -> CT:
        return self._reader.read_config(meta_config=self._meta_config)

    def load_random_config(self, *, rng: Random) -> CT:
        return self.build_config(
            meta_config=self._meta_config,
            mutable_meta_config=rng.choice(self._mutable_meta_config_pool),
            rng=rng,
        )

    @abstractmethod
    def build_config(self, *, meta_config: MT, mutable_meta_config: UT, rng: Random) -> CT: ...
