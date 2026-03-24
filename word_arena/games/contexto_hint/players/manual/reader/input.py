from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import ContextoHintFeedback, ContextoHintGuess

type ContextoHintGameStateInterface = ManualGameStateInterface[
    list[str], ContextoHintGuess, ContextoHintFeedback
]


class ContextoHintInputManualReader(
    BaseInputManualReader[str, list[str], ContextoHintGuess, ContextoHintFeedback]
):
    @override
    def input_guess(
        self, *, game_state: ContextoHintGameStateInterface, input_func: Callable[[str], str]
    ) -> ContextoHintGuess:
        guess: str = input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        return ContextoHintGuess(index=int(guess) if guess.isdigit() else -1)
