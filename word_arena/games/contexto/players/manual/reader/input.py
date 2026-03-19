from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import ContextoGuess


class ContextoInputManualReader(BaseInputManualReader[ContextoGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> ContextoGuess:
        return ContextoGuess(word=input_func(f"Input word for guess {turn_id + 1}: "))
