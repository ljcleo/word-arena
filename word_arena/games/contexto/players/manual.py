from ....common.player.manual import BaseManualPlayer
from ..common import ContextoFeedback
from ..formatter import ContextoInGameFormatter
from .log import ContextoLogPlayer


class ContextoManualPlayer(BaseManualPlayer[int, None, str, ContextoFeedback], ContextoLogPlayer):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ContextoInGameFormatter)
