from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig
from ..generators.provider import ContextoGameProvider
from ..players.manual import ContextoManualPlayer
from .base import ContextoConfigGym


class ContextoManualGym(
    BaseManualGym[ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult],
    ContextoConfigGym[[]],
):
    def __init__(self) -> None:
        super().__init__(game_provider=ContextoGameProvider())

    @override
    def create_player(self) -> ContextoManualPlayer:
        return ContextoManualPlayer()
