from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import RedactleConfig
from .common import RedactleMetaConfig


class RedactleConfigGenerator(BaseConfigGenerator[RedactleMetaConfig, int, RedactleConfig]):
    @override
    def __call__(
        self, *, meta_config: RedactleMetaConfig, mutable_meta_config: int, rng: Random
    ) -> RedactleConfig:
        return RedactleConfig(
            data_file=meta_config.data_file,
            stop_words=meta_config.stop_words,
            game_id=meta_config.random_game_id(rng=rng),
            max_turns=mutable_meta_config,
        )
