from collections.abc import Callable
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..generators.common import LetrosoConfig
from ..generators.provider import LetrosoGameProvider
from ..players.manual import LetrosoManualPlayer
from .base import LetrosoConfigGym


class LetrosoManualGym(
    BaseManualGym[
        LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
    ],
    LetrosoConfigGym[[Callable[[str], str], Callable[[str], None]]],
):
    def __init__(
        self,
        *,
        create_config_func: Callable[[], LetrosoConfig],
        log_func: Callable[[str], None],
    ) -> None:
        super().__init__(
            game_provider=LetrosoGameProvider(),
            create_config_func=create_config_func,
            log_func=log_func,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> LetrosoManualPlayer:
        return LetrosoManualPlayer(input_func=input_func, player_log_func=player_log_func)
