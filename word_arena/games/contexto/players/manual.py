from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ContextoFeedback, ContextoGuess
from ..formatter import ContextoInGameFormatter


class ContextoManualPlayer(BaseManualPlayer[int, None, ContextoGuess, ContextoFeedback]):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ContextoInGameFormatter)

    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> ContextoGuess:
        return ContextoGuess(word=guess_str)
