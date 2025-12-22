from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import LetrosoFeedback, LetrosoGuess, LetrosoInfo
from ..formatters.base import LetrosoInGameFormatter


class LetrosoManualPlayer(
    BaseManualPlayer[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback], LetrosoInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> LetrosoGuess:
        return LetrosoGuess(word=guess_str)
