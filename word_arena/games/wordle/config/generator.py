from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import WordleConfig
from .common import WordleMetaConfig, WordleMutableMetaConfig


class WordleConfigGenerator(
    BaseConfigGenerator[WordleMetaConfig, WordleMutableMetaConfig, WordleConfig]
):
    @override
    def __call__(
        self,
        *,
        meta_config: WordleMetaConfig,
        mutable_meta_config: WordleMutableMetaConfig,
        rng: Random,
    ) -> WordleConfig:
        return WordleConfig(
            word_pool=meta_config.word_pool,
            max_turns=mutable_meta_config.max_turns,
            game_ids=meta_config.random_game_ids(count=mutable_meta_config.num_targets, rng=rng),
        )
