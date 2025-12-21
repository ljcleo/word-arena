from ..common import LetrosoFeedback, LetrosoInfo
from .log import LetrosoLogPlayer
from ..formatter import LetrosoInGameFormatter
from ....common.player.manual import BaseManualPlayer


class LetrosoManualPlayer(
    BaseManualPlayer[LetrosoInfo, None, str, LetrosoFeedback], LetrosoLogPlayer
):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=LetrosoInGameFormatter)
