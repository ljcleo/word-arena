from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import StrandsConfig
from .common import StrandsMetaConfig


class StrandsConfigGenerator(BaseConfigGenerator[StrandsMetaConfig, int, StrandsConfig]):
    @override
    def __call__(
        self, *, meta_config: StrandsMetaConfig, mutable_meta_config: int, rng: Random
    ) -> StrandsConfig:
        return StrandsConfig(
            data_file=meta_config.data_file,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
