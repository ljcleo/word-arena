from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoHintGuess
from ..generators.common import ContextoHintConfig
from ..generators.provider import ContextoHintGameProvider
from ..players.manual import ContextoHintManualPlayer
from .base import ContextoHintConfigGym, ContextoHintExampleConfigGym


class ContextoHintManualGym(
    ContextoHintConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[Path, ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str]],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func, game_provider=ContextoHintGameProvider(data_file=data_file), **kwargs
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> ContextoHintManualPlayer:
        return ContextoHintManualPlayer(input_func=input_func, player_log_func=player_log_func)


class ContextoHintExampleManualGym(ContextoHintExampleConfigGym, ContextoHintManualGym):
    def __init__(
        self, *, data_file: Path, log_func: Callable[[str], None], input_func: Callable[[str], str]
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)
