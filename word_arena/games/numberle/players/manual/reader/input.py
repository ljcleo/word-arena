from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import NumberleFeedback, NumberleGuess, NumberleInfo

type NumberleGameStateInterface = ManualGameStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback
]


class NumberleInputManualReader(
    BaseInputManualReader[str, NumberleInfo, NumberleGuess, NumberleFeedback]
):
    @override
    def input_guess(
        self, *, game_state: NumberleGameStateInterface, input_func: Callable[[str], str]
    ) -> NumberleGuess:
        return NumberleGuess(
            equation=input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        )
