from random import Random
from typing import Iterable, override

from ....common.generator.generator import BaseGameGenerator
from ..game import ContextoGame
from .common import ContextoConfig, get_contexto_game_count
from .provider import ContextoGameProvider


class ContextoGameGenerator(
    ContextoGameProvider, BaseGameGenerator[None, int, ContextoConfig, ContextoGame]
):
    def __init__(self, *, mutable_meta_config_pool: Iterable[int], seed: int, **kwargs) -> None:
        super().__init__(mutable_meta_config_pool=mutable_meta_config_pool, seed=seed, **kwargs)

    @override
    def generate_config(
        self, *, meta_config: None, mutable_meta_config: int, rng: Random
    ) -> ContextoConfig:
        return ContextoConfig(
            max_guesses=mutable_meta_config, game_id=rng.randrange(get_contexto_game_count())
        )
