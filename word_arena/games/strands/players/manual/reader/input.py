from collections.abc import Callable
from typing import override

from pydantic import TypeAdapter

from ......players.manual.reader.input import BaseInputManualReader
from ....common import StrandsGuess


class StrandsInputManualReader(BaseInputManualReader[StrandsGuess]):
    @override
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> StrandsGuess:
        return StrandsGuess(
            coords=[
                TypeAdapter(tuple[int, int]).validate_json(
                    coord_str.strip().replace("(", "[").replace(")", "]")
                )
                for coord_str in input_func(
                    f"Input coord list for guess {turn_id + 1}; "
                    "use `(x, y)` for coords and connecting them with `->`: "
                ).split("->")
            ]
        )
