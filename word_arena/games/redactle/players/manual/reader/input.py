from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import RedactleFeedback, RedactleGuess, RedactleInfo


class RedactleInputManualReader(
    BaseInputManualReader[str, RedactleInfo, RedactleGuess, RedactleFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        input_func: Callable[[str], str],
    ) -> RedactleGuess:
        return RedactleGuess(
            word=input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        )
