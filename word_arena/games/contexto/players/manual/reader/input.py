from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import ContextoFeedback, ContextoGuess


class ContextoInputManualReader(BaseInputManualReader[str, int, ContextoGuess, ContextoFeedback]):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        input_func: Callable[[str], str],
    ) -> ContextoGuess:
        return ContextoGuess(
            word=input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        )
