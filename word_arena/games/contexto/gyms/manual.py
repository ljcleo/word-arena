from collections.abc import Callable
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig
from ..generators.provider import ContextoGameProvider
from ..players.manual import ContextoManualPlayer
from .base import ContextoConfigGym, ContextoExampleConfigGym


class ContextoManualGym(
    ContextoConfigGym[[Callable[[str], str], Callable[[str, str], None]]],
    BaseManualGym[
        None, ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult
    ],
):
    def __init__(self, *, log_func: Callable[[str, str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func, game_provider=ContextoGameProvider(meta_config=None), **kwargs
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str, str], None]
    ) -> ContextoManualPlayer:
        return ContextoManualPlayer(input_func=input_func, player_log_func=player_log_func)


class ContextoExampleManualGym(ContextoExampleConfigGym, ContextoManualGym):
    def __init__(
        self, *, log_func: Callable[[str, str], None], input_func: Callable[[str], str]
    ) -> None:
        super().__init__(log_func=log_func, input_func=input_func)
