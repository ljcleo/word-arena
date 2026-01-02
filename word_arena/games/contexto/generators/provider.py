from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import ContextoGame
from .common import ContextoConfig


class ContextoGameProvider(BaseGameProvider[None, ContextoConfig, ContextoGame]):
    @override
    def create_game(self, *, meta_config: None, config: ContextoConfig) -> ContextoGame:
        return ContextoGame(max_guesses=config.max_guesses, game_id=config.game_id)
