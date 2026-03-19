from random import Random
from typing import override

from ....common.config.loader.base import BaseConfigLoader
from ..common import ContextoHintConfig
from .common import ContextoHintMetaConfig


class ContextoHintConfigLoader(BaseConfigLoader[ContextoHintMetaConfig, int, ContextoHintConfig]):
    @override
    def build_config(
        self, *, meta_config: ContextoHintMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ContextoHintConfig:
        return ContextoHintConfig(
            data_file=meta_config.data_file,
            num_candidates=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
