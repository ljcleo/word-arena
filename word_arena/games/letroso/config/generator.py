from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import LetrosoConfig
from .common import LetrosoMetaConfig, LetrosoMutableMetaConfig


class LetrosoConfigGenerator(
    BaseConfigGenerator[LetrosoMetaConfig, LetrosoMutableMetaConfig, LetrosoConfig]
):
    @override
    def __call__(
        self,
        *,
        meta_config: LetrosoMetaConfig,
        mutable_meta_config: LetrosoMutableMetaConfig,
        rng: Random,
    ) -> LetrosoConfig:
        return LetrosoConfig(
            word_pool=meta_config.word_pool,
            max_letters=mutable_meta_config.max_letters,
            max_turns=mutable_meta_config.max_turns,
            game_ids=meta_config.random_game_ids(count=mutable_meta_config.num_targets, rng=rng),
        )
