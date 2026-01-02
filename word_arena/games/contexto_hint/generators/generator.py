from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ContextoHintGame
from .common import ContextoHintConfig, ContextoHintMetaConfig
from .provider import ContextoHintGameProvider


class ContextoHintGameGenerator(
    ContextoHintGameProvider,
    BaseGameGenerator[ContextoHintMetaConfig, int, ContextoHintConfig, ContextoHintGame],
):
    @override
    def generate_config(
        self, *, meta_config: ContextoHintMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ContextoHintConfig:
        return ContextoHintConfig(
            num_candidates=mutable_meta_config, game_id=meta_config.random_game_id(rng=rng)
        )
