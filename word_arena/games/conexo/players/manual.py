from ....common.player.manual import BaseManualPlayer
from ..common import ConexoFeedback, ConexoInfo
from ..formatter import ConexoInGameFormatter
from .log import ConexoLogPlayer


class ConexoManualPlayer(
    BaseManualPlayer[ConexoInfo, None, set[int], ConexoFeedback], ConexoLogPlayer
):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ConexoInGameFormatter)
