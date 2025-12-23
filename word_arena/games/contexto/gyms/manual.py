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
    ContextoConfigGym[[Callable[[str], str], Callable[[str], None]]],
):
    def __init__(
        self,
        *,
        create_config_func: Callable[[], ContextoConfig],
        log_func: Callable[[str], None],
    ) -> None:
        super().__init__(
            game_provider=ContextoGameProvider(),
            create_config_func=create_config_func,
            log_func=log_func,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> ContextoManualPlayer:
        return ContextoManualPlayer(input_func=input_func, player_log_func=player_log_func)
