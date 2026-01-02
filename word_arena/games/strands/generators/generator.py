from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import StrandsGame
from .common import StrandsConfig, StrandsMetaConfig
from .provider import StrandsGameProvider


class StrandsGameGenerator(
    StrandsGameProvider, BaseGameGenerator[StrandsMetaConfig, int, StrandsConfig, StrandsGame]
):
    @override
    def generate_config(
        self, *, meta_config: StrandsMetaConfig, mutable_meta_config: int, rng: Random
    ) -> StrandsConfig:
        return StrandsConfig(
            max_guesses=mutable_meta_config, game_id=meta_config.random_game_id(rng=rng)
        )
