from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import ContextoGame
from .common import ContextoConfig


class ContextoGameProvider(BaseGameProvider[ContextoConfig, ContextoGame]):
    @override
    def create_game(self, *, config: ContextoConfig) -> ContextoGame:
        return ContextoGame(game_id=config.game_id, max_guesses=config.max_guesses)
