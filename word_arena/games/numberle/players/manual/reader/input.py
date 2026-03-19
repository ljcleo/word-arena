from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import NumberleGuess


class NumberleInputManualReader(BaseInputManualReader[NumberleGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> NumberleGuess:
        return NumberleGuess(equation=input_func(f"Input equation for guess {turn_id + 1}: "))
