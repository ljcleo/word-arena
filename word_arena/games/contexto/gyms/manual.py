from collections.abc import Callable
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..generators.common import ContextoConfig
from ..generators.provider import ContextoGameProvider
from ..players.manual import ContextoManualPlayer
from .base import ContextoConfigGym


class ContextoManualGym(
    ContextoConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[
        None, ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult
    ],
):
    def __init__(
        self, *, log_func: Callable[[str], None], config_creator: Callable[[], ContextoConfig]
    ) -> None:
        super().__init__(
            log_func=log_func, config_creator=config_creator, game_provider=ContextoGameProvider()
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> ContextoManualPlayer:
        return ContextoManualPlayer(input_func=input_func, player_log_func=player_log_func)
