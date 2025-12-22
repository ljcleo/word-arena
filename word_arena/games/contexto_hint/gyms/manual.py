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
    ContextoHintConfigGym[[]],
):
    def __init__(self, *, games_dir: Path) -> None:
        super().__init__(game_provider=ContextoHintGameProvider(games_dir=games_dir))

    @override
    def create_player(self) -> ContextoHintManualPlayer:
        return ContextoHintManualPlayer()
