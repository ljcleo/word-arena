from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import WordleFeedback, WordleGuess, WordleInfo
from ..formatters.base import WordleInGameFormatter


class WordleManualPlayer(
    BaseManualPlayer[WordleInfo, None, WordleGuess, WordleFeedback], WordleInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> WordleGuess:
        return WordleGuess(word=guess_str)
