from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import WordleFeedback, WordleGuess, WordleInfo

type WordleGameStateInterface = ManualGameStateInterface[WordleInfo, WordleGuess, WordleFeedback]


class WordleInputManualReader(BaseInputManualReader[str, WordleInfo, WordleGuess, WordleFeedback]):
    @override
    def input_guess(
        self, *, game_state: WordleGameStateInterface, input_func: Callable[[str], str]
    ) -> WordleGuess:
        return WordleGuess(
            word=input_func(self.prompt_config.format(turn_id=len(game_state.turns) + 1))
        )
