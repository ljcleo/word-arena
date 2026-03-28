from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import WordleFeedback, WordleGuess, WordleInfo


class WordleInputManualReader(BaseInputManualReader[str, WordleInfo, WordleGuess, WordleFeedback]):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        input_func: Callable[[str], str],
    ) -> WordleGuess:
        return WordleGuess(
            word=input_func(self.prompt_config.format(turn_id=len(trajectory.turns) + 1))
        )
