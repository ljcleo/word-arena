from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import ConexoConfig
from .common import ConexoMetaConfig


class ConexoConfigGenerator(BaseConfigGenerator[ConexoMetaConfig, int, ConexoConfig]):
    @override
    def __call__(
        self, *, meta_config: ConexoMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ConexoConfig:
        return ConexoConfig(
            data_file=meta_config.data_file,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
