from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import LetrosoFeedback, LetrosoGuess, LetrosoInfo


class LetrosoInputManualReader(
    BaseInputManualReader[str, LetrosoInfo, LetrosoGuess, LetrosoFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        input_func: Callable[[str], str],
    ) -> LetrosoGuess:
        return LetrosoGuess(
            word=input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        )
