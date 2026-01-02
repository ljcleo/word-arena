from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import WordleGame
from .common import WordleConfig, WordleMetaConfig, WordleMutableMetaConfig
from .provider import WordleGameProvider


class WordleGameGenerator(
    WordleGameProvider,
    BaseGameGenerator[WordleMetaConfig, WordleMutableMetaConfig, WordleConfig, WordleGame],
):
    @override
    def generate_config(
        self,
        *,
        meta_config: WordleMetaConfig,
        mutable_meta_config: WordleMutableMetaConfig,
        rng: Random,
    ) -> WordleConfig:
        return WordleConfig(
            max_guesses=mutable_meta_config.max_guesses,
            game_ids=meta_config.random_game_ids(count=mutable_meta_config.num_targets, rng=rng),
        )
