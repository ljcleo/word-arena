from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import NumberleFeedback, NumberleGuess, NumberleInfo


class NumberleInputManualReader(
    BaseInputManualReader[str, NumberleInfo, NumberleGuess, NumberleFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        input_func: Callable[[str], str],
    ) -> NumberleGuess:
        return NumberleGuess(
            equation=input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        )
