from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ConexoFeedback, ConexoGuess, ConexoInfo
from ..formatters.base import ConexoInGameFormatter


class ConexoManualPlayer(
    BaseManualPlayer[ConexoInfo, None, ConexoGuess, ConexoFeedback], ConexoInGameFormatter
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> ConexoGuess:
        return ConexoGuess(
            indices=[int(guess) if guess.isdigit() else -1 for guess in guess_str.strip().split()]
        )
