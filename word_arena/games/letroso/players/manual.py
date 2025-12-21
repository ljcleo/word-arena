from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import LetrosoFeedback, LetrosoGuess, LetrosoInfo
from ..formatter import LetrosoInGameFormatter


class LetrosoManualPlayer(BaseManualPlayer[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback]):
    def __init__(self) -> None:
        super().__init__(in_game_formatter_cls=LetrosoInGameFormatter)

    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> LetrosoGuess:
        return LetrosoGuess(word=guess_str)
