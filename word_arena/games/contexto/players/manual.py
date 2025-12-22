from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ContextoFeedback, ContextoGuess
from ..formatters.base import ContextoInGameFormatter


class ContextoManualPlayer(
    BaseManualPlayer[int, None, ContextoGuess, ContextoFeedback], ContextoInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> ContextoGuess:
        return ContextoGuess(word=guess_str)
