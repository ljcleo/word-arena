from random import Random
from typing import override

from .....common.game.config.loader.base import BaseConfigLoader
from ..common import StrandsConfig, StrandsMetaConfig


class StrandsConfigLoader(BaseConfigLoader[StrandsMetaConfig, int, StrandsConfig]):
    @override
    def build_config(
        self, *, meta_config: StrandsMetaConfig, mutable_meta_config: int, rng: Random
    ) -> StrandsConfig:
        return StrandsConfig(
            data_file=meta_config.data_file,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
