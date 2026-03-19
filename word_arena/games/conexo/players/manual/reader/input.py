from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ....common import ConexoGuess


class ConexoInputManualReader(BaseInputManualReader[ConexoGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> ConexoGuess:
        return ConexoGuess(
            indices=[
                int(guess) if guess.isdigit() else -1
                for guess in input_func(
                    f"Input word IDs for guess {turn_id + 1} (separated by spaces): "
                )
                .strip()
                .split()
            ]
        )
