from collections.abc import Callable
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
    ConexoConfigGym[[Callable[[str], str], Callable[[str], None]]],
):
    def __init__(
        self,
        *,
        games_dir: Path,
        create_config_func: Callable[[], ConexoConfig],
        log_func: Callable[[str], None],
    ) -> None:
        super().__init__(
            game_provider=ConexoGameProvider(games_dir=games_dir),
            create_config_func=create_config_func,
            log_func=log_func,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> ConexoManualPlayer:
        return ConexoManualPlayer(input_func=input_func, player_log_func=player_log_func)
