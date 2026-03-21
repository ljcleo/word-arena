from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import NumberleConfig
from .common import NumberleMetaConfig, NumberleMutableMetaConfig


class NumberleConfigGenerator(
    BaseConfigGenerator[NumberleMetaConfig, NumberleMutableMetaConfig, NumberleConfig]
):
    @override
    def __call__(
        self,
        *,
        meta_config: NumberleMetaConfig,
        mutable_meta_config: NumberleMutableMetaConfig,
        rng: Random,
    ) -> NumberleConfig:
        return NumberleConfig(
            data_file=meta_config.data_file,
            eq_pool=meta_config.eq_pool,
            eq_length=mutable_meta_config.eq_length,
            max_turns=mutable_meta_config.max_turns,
            game_ids=meta_config.random_game_ids(
                eq_length=mutable_meta_config.eq_length,
                count=mutable_meta_config.num_targets,
                rng=rng,
            ),
        )
