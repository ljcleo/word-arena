from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import ContextoHintFeedback, ContextoHintGuess


class ContextoHintInputManualReader(
    BaseInputManualReader[str, list[str], ContextoHintGuess, ContextoHintFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        input_func: Callable[[str], str],
    ) -> ContextoHintGuess:
        guess: str = input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        return ContextoHintGuess(index=int(guess) if guess.isdigit() else -1)
