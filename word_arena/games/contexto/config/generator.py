from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import ContextoConfig
from .common import ContextoMetaConfig


class ContextoConfigGenerator(BaseConfigGenerator[ContextoMetaConfig, int, ContextoConfig]):
    @override
    def __call__(
        self, *, meta_config: ContextoMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ContextoConfig:
        return ContextoConfig(
            base_url=meta_config.base_url,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
