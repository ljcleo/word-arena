from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import NumberleGame
from .common import NumberleConfig, NumberleMetaConfig, NumberleMutableMetaConfig
from .provider import NumberleGameProvider


class NumberleGameGenerator(
    NumberleGameProvider,
    BaseGameGenerator[NumberleMetaConfig, NumberleMutableMetaConfig, NumberleConfig, NumberleGame],
):
    @override
    def generate_config(
        self,
        *,
        meta_config: NumberleMetaConfig,
        mutable_meta_config: NumberleMutableMetaConfig,
        rng: Random,
    ) -> NumberleConfig:
        return NumberleConfig(
            eq_length=mutable_meta_config.eq_length,
            max_guesses=mutable_meta_config.max_guesses,
            game_ids=meta_config.random_game_ids(
                eq_length=mutable_meta_config.eq_length,
                count=mutable_meta_config.num_targets,
                rng=rng,
            ),
        )
