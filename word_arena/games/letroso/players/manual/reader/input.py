from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import LetrosoFeedback, LetrosoGuess, LetrosoInfo

type LetrosoGameStateInterface = ManualGameStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback
]


class LetrosoInputManualReader(
    BaseInputManualReader[str, LetrosoInfo, LetrosoGuess, LetrosoFeedback]
):
    @override
    def input_guess(
        self, *, game_state: LetrosoGameStateInterface, input_func: Callable[[str], str]
    ) -> LetrosoGuess:
        return LetrosoGuess(
            word=input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        )
