from collections.abc import Callable
from typing import override

from ......players.manual.reader.input import BaseInputManualReader
from ......players.manual.state import ManualGameStateInterface
from ....common import ConnectionsFeedback, ConnectionsGuess, ConnectionsInfo

type ConnectionsGameStateInterface = ManualGameStateInterface[
    ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback
]


class ConnectionsInputManualReader(
    BaseInputManualReader[str, ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback]
):
    @override
    def input_guess(
        self, *, game_state: ConnectionsGameStateInterface, input_func: Callable[[str], str]
    ) -> ConnectionsGuess:
        turn_id: int = len(game_state.turns) + 1
        indices: list[int] = []

        for i in range(4):
            guess: str = input_func(self.prompt_config.format(turn_id=turn_id, word_id=i + 1))
            indices.append(int(guess) if guess.isdigit() else -1)

        return ConnectionsGuess(indices=indices)
