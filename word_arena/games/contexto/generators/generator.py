from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ContextoGame
from .common import ContextoConfig, random_game_id
from .provider import ContextoGameProvider


class ContextoGameGenerator(
    ContextoGameProvider, BaseGameGenerator[None, int, ContextoConfig, ContextoGame]
):
    @override
    def generate_config(
        self, *, meta_config: None, mutable_meta_config: int, rng: Random
    ) -> ContextoConfig:
        return ContextoConfig(max_guesses=mutable_meta_config, game_id=random_game_id(rng=rng))
