from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import WordleFeedback, WordleGuess, WordleInfo
from ..formatter import WordleInGameFormatter


class WordleManualPlayer(
    BaseManualPlayer[WordleInfo, None, WordleGuess, WordleFeedback]
):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=WordleInGameFormatter)

    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> WordleGuess:
        return WordleGuess(word=guess_str)
