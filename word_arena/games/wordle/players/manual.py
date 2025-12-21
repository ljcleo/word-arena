from ....common.player.manual import BaseManualPlayer
from ..common import WordleFeedback, WordleInfo
from ..formatter import WordleInGameFormatter
from .log import WordleLogPlayer


class WordleManualPlayer(BaseManualPlayer[WordleInfo, None, str, WordleFeedback], WordleLogPlayer):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=WordleInGameFormatter)
