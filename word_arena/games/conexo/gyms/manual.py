from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..generators.common import ConexoConfig, ConexoMetaConfig
from ..generators.provider import ConexoGameProvider
from ..players.manual import ConexoManualPlayer
from .base import ConexoConfigGym, ConexoExampleConfigGym


class ConexoManualGym(
    ConexoConfigGym[[Callable[[str], str], Callable[[str], None]]],
    BaseManualGym[
        ConexoMetaConfig,
        ConexoConfig,
        ConexoInfo,
        None,
        ConexoGuess,
        ConexoFeedback,
        ConexoFinalResult,
    ],
):
    def __init__(self, *, data_file: Path, log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(
            log_func=log_func,
            game_provider=ConexoGameProvider(meta_config=ConexoMetaConfig(data_file=data_file)),
            **kwargs,
        )

    @override
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> ConexoManualPlayer:
        return ConexoManualPlayer(input_func=input_func, player_log_func=player_log_func)


class ConexoExampleManualGym(ConexoExampleConfigGym, ConexoManualGym):
    def __init__(
        self, *, data_file: Path, log_func: Callable[[str], None], input_func: Callable[[str], str]
    ) -> None:
        super().__init__(data_file=data_file, log_func=log_func, input_func=input_func)
