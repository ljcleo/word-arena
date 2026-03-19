from random import Random
from typing import override

from ....common.config.loader.base import BaseConfigLoader
from ..common import ContextoConfig
from .common import ContextoMetaConfig


class ContextoConfigLoader(BaseConfigLoader[ContextoMetaConfig, int, ContextoConfig]):
    @override
    def build_config(
        self, *, meta_config: ContextoMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ContextoConfig:
        return ContextoConfig(
            base_url=meta_config.base_url,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
