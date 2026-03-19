from random import Random
from typing import override

from .....common.game.config.loader.base import BaseConfigLoader
from ..common import ConexoConfig, ConexoMetaConfig


class ConexoConfigLoader(BaseConfigLoader[ConexoMetaConfig, int, ConexoConfig]):
    @override
    def build_config(
        self, *, meta_config: ConexoMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ConexoConfig:
        return ConexoConfig(
            data_file=meta_config.data_file,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
