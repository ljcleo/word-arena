from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import NumberleFeedback, NumberleGuess, NumberleInfo
from ..formatters.base import NumberleInGameFormatter


class NumberleManualPlayer(
    BaseManualPlayer[NumberleInfo, None, NumberleGuess, NumberleFeedback], NumberleInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> NumberleGuess:
        return NumberleGuess(equation=guess_str)
