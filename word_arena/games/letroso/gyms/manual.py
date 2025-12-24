from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..generators.common import LetrosoConfig, LetrosoMetaConfig
from ..generators.provider import LetrosoGameProvider
from ..players.manual import LetrosoManualPlayer
from .base import LetrosoConfigGym


class LetrosoManualGym(
    LetrosoConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[
        LetrosoMetaConfig,
        LetrosoConfig,
        LetrosoInfo,
        None,
        LetrosoGuess,
        LetrosoFeedback,
        LetrosoFinalResult,
    ],
):
    def __init__(
        self,
        *,
        data_file: Path,
        log_func: Callable[[str], None],
        config_creator: Callable[[], LetrosoConfig],
    ) -> None:
        super().__init__(
            log_func=log_func,
            config_creator=config_creator,
            game_provider=LetrosoGameProvider(data_file=data_file),
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> LetrosoManualPlayer:
        return LetrosoManualPlayer(input_func=input_func, player_log_func=player_log_func)
