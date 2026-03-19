from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import LetrosoGuess


class LetrosoInputManualReader(BaseInputManualReader[LetrosoGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> LetrosoGuess:
        return LetrosoGuess(word=input_func(f"Input word for guess {turn_id + 1}: "))
