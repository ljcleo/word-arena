from typing import override

from ....common.game.loader.base import BaseGameLoader
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from .common import ContextoConfig
from .engine import ContextoGameEngine


class ContextoGameLoader(
    BaseGameLoader[ContextoConfig, int, ContextoGuess, ContextoFeedback, ContextoFinalResult]
):
    @override
    def create_engine(self, *, config: ContextoConfig) -> ContextoGameEngine:
        return ContextoGameEngine(max_turns=config.max_turns, game_id=config.game_id)
