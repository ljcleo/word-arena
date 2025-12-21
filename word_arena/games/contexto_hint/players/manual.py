from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ContextoHintGuess
from ..formatter import ContextoHintInGameFormatter


class ContextoHintManualPlayer(BaseManualPlayer[None, list[str], ContextoHintGuess, int]):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=ContextoHintInGameFormatter)

    @override
    def parse_guess(self, *, hint: list[str], guess_str: str) -> ContextoHintGuess:
        return ContextoHintGuess(index=int(guess_str) if guess_str.isdigit() else -1)
