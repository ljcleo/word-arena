from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ContextoHintGuess
from ..generators.common import ContextoHintConfig
from ..generators.provider import ContextoHintGameProvider
from ..players.manual import ContextoHintManualPlayer
from .base import ContextoHintConfigGym


class ContextoHintManualGym(
    BaseManualGym[ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str]],
    ContextoHintConfigGym[[Callable[[str], str]]],
):
    def __init__(
        self, *, games_dir: Path, create_config_func: Callable[[], ContextoHintConfig]
    ) -> None:
        super().__init__(
            game_provider=ContextoHintGameProvider(games_dir=games_dir),
            create_config_func=create_config_func,
        )

    @override
    def create_player(self, *, input_func: Callable[[str], str]) -> ContextoHintManualPlayer:
        return ContextoHintManualPlayer(input_func=input_func)
