from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ConexoGame
from .common import ConexoConfig, ConexoMetaConfig
from .provider import ConexoGameProvider


class ConexoGameGenerator(
    ConexoGameProvider, BaseGameGenerator[ConexoMetaConfig, int, ConexoConfig, ConexoGame]
):
    @override
    def generate_config(
        self, *, meta_config: ConexoMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ConexoConfig:
        return ConexoConfig(
            max_guesses=mutable_meta_config, game_id=meta_config.random_game_id(rng=rng)
        )
