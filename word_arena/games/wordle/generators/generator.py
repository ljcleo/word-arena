from pathlib import Path
from random import Random
from typing import Iterable, override

from ....common.generator.generator import BaseGameGenerator
from ..game import WordleGame
from .common import WordleConfig, WordleMetaConfig, WordleMutableMetaConfig
from .provider import WordleGameProvider


class WordleGameGenerator(
    WordleGameProvider,
    BaseGameGenerator[WordleMetaConfig, WordleMutableMetaConfig, WordleConfig, WordleGame],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[WordleMutableMetaConfig],
        seed: int,
        **kwargs,
    ) -> None:
        super().__init__(
            data_file=data_file,
            mutable_meta_config_pool=mutable_meta_config_pool,
            seed=seed,
            **kwargs,
        )

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
            game_ids=rng.sample(
                range(len(meta_config.target_pool)), mutable_meta_config.num_targets
            ),
        )
