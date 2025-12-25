from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo
from ..generators.common import NumberleConfig, NumberleMetaConfig
from ..generators.provider import NumberleGameProvider
from ..players.manual import NumberleManualPlayer
from .base import NumberleConfigGym, NumberleExampleConfigGym


class NumberleManualGym(
    NumberleConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[
        NumberleMetaConfig,
        NumberleConfig,
        NumberleInfo,
        None,
        NumberleGuess,
        NumberleFeedback,
        NumberleFinalResult,
    ],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func, game_provider=NumberleGameProvider(data_file=data_file), **kwargs
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> NumberleManualPlayer:
        return NumberleManualPlayer(input_func=input_func, player_log_func=player_log_func)


class NumberleExampleManualGym(NumberleExampleConfigGym, NumberleManualGym):
    def __init__(
        self, *, data_file: Path, log_func: Callable[[str], None], input_func: Callable[[str], str]
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)
