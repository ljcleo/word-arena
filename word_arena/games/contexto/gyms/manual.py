from collections.abc import Callable
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig
from ..generators.provider import ContextoGameProvider
from ..players.manual import ContextoManualPlayer
from .base import ContextoConfigGym


class ContextoManualGym(
    BaseManualGym[ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult],
    ContextoConfigGym[[Callable[[str], str]]],
):
    def __init__(self, *, create_config_func: Callable[[], ContextoConfig]) -> None:
        super().__init__(
            game_provider=ContextoGameProvider(), create_config_func=create_config_func
        )

    @override
    def create_player(self, *, input_func: Callable[[str], str]) -> ContextoManualPlayer:
        return ContextoManualPlayer(input_func=input_func)
