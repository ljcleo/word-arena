from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ContextoHintGuess
from ..formatters.base import ContextoHintInGameFormatter


class ContextoHintManualPlayer(
    BaseManualPlayer[None, list[str], ContextoHintGuess, int], ContextoHintInGameFormatter
):
    @override
    def parse_guess(self, *, hint: list[str], guess_str: str) -> ContextoHintGuess:
        return ContextoHintGuess(index=int(guess_str) if guess_str.isdigit() else -1)
