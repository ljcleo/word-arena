from typing import override

from pydantic import TypeAdapter

from ....common.player.manual import BaseManualPlayer
from ..common import StrandsFeedback, StrandsGuess, StrandsInfo
from ..formatters.base import StrandsInGameFormatter


class StrandsManualPlayer(
    BaseManualPlayer[StrandsInfo, None, StrandsGuess, StrandsFeedback],
    StrandsInGameFormatter,
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> StrandsGuess:
        return StrandsGuess(
            coords=[
                TypeAdapter(tuple[int, int]).validate_json(
                    coord_str.replace("(", "[").replace(")", "]")
                )
                for coord_str in guess_str.split("->")
            ]
        )
