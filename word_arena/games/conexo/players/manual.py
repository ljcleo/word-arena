from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ConexoFeedback, ConexoGuess, ConexoInfo
from ..formatter import ConexoInGameFormatter


class ConexoManualPlayer(BaseManualPlayer[ConexoInfo, None, ConexoGuess, ConexoFeedback]):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ConexoInGameFormatter)

    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> ConexoGuess:
        return ConexoGuess(
            indices=[int(guess) if guess.isdigit() else -1 for guess in guess_str.strip().split()]
        )
