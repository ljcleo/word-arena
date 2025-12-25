from pathlib import Path
from random import Random
from typing import Iterable, override

from ....common.generator.generator import BaseGameGenerator
from ..game import NumberleGame
from .common import NumberleConfig, NumberleMetaConfig, NumberleMutableMetaConfig
from .provider import NumberleGameProvider


class NumberleGameGenerator(
    NumberleGameProvider,
    BaseGameGenerator[NumberleMetaConfig, NumberleMutableMetaConfig, NumberleConfig, NumberleGame],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[NumberleMutableMetaConfig],
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
        meta_config: NumberleMetaConfig,
        mutable_meta_config: NumberleMutableMetaConfig,
        rng: Random,
    ) -> NumberleConfig:
        return NumberleConfig(
            eq_length=mutable_meta_config.eq_length,
            max_guesses=mutable_meta_config.max_guesses,
            game_ids=rng.sample(
                range(meta_config.get_game_count(eq_length=mutable_meta_config.eq_length)),
                mutable_meta_config.num_targets,
            ),
        )
