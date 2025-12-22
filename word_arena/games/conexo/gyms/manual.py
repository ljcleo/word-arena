from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..generators.common import ConexoConfig
from ..generators.provider import ConexoGameProvider
from ..players.manual import ConexoManualPlayer
from .base import ConexoConfigGym


class ConexoManualGym(
    BaseManualGym[ConexoConfig, ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult],
    ConexoConfigGym[[]],
):
    def __init__(self, *, games_dir: Path) -> None:
        super().__init__(game_provider=ConexoGameProvider(games_dir=games_dir))

    @override
    def create_player(self) -> ConexoManualPlayer:
        return ConexoManualPlayer()
