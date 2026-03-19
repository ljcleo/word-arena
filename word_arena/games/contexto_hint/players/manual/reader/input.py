from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import ContextoHintGuess


class ContextoHintInputManualReader(BaseInputManualReader[ContextoHintGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> ContextoHintGuess:
        guess_str: str = input_func(f"Input index for guess {turn_id + 1}: ")
        return ContextoHintGuess(index=int(guess_str) if guess_str.isdigit() else -1)
