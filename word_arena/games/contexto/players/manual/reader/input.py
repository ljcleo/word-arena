from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import ContextoFeedback, ContextoGuess

type ContextoGameStateInterface = ManualGameStateInterface[int, ContextoGuess, ContextoFeedback]


class ContextoInputManualReader(BaseInputManualReader[str, int, ContextoGuess, ContextoFeedback]):
    @override
    def input_guess(
        self, *, game_state: ContextoGameStateInterface, input_func: Callable[[str], str]
    ) -> ContextoGuess:
        return ContextoGuess(
            word=input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        )
