from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import RedactleFeedback, RedactleGuess, RedactleInfo

type RedactleGameStateInterface = ManualGameStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback
]


class RedactleInputManualReader(
    BaseInputManualReader[str, RedactleInfo, RedactleGuess, RedactleFeedback]
):
    @override
    def input_guess(
        self, *, game_state: RedactleGameStateInterface, input_func: Callable[[str], str]
    ) -> RedactleGuess:
        return RedactleGuess(
            word=input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        )
