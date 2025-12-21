from ....common.player.manual import BaseManualPlayer
from ..formatter import ContextoHintInGameFormatter
from .log import ContextoHintLogPlayer


class ContextoHintManualPlayer(BaseManualPlayer[None, list[str], int, int], ContextoHintLogPlayer):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ContextoHintInGameFormatter)
