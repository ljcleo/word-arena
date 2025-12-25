from pathlib import Path
from random import Random
from typing import Iterable, override

from ....common.generator.generator import BaseGameGenerator
from ..game import LetrosoGame
from .common import LetrosoConfig, LetrosoMetaConfig, LetrosoMutableMetaConfig
from .provider import LetrosoGameProvider


class LetrosoGameGenerator(
    LetrosoGameProvider,
    BaseGameGenerator[LetrosoMetaConfig, LetrosoMutableMetaConfig, LetrosoConfig, LetrosoGame],
):
    def __init__(
        self,
        *,
        data_file: Path,
        mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig],
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
        meta_config: LetrosoMetaConfig,
        mutable_meta_config: LetrosoMutableMetaConfig,
        rng: Random,
    ) -> LetrosoConfig:
        return LetrosoConfig(
            max_letters=mutable_meta_config.max_letters,
            max_guesses=mutable_meta_config.max_guesses,
            game_ids=rng.sample(range(meta_config.game_count), mutable_meta_config.num_targets),
        )
