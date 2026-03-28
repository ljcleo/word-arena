from collections.abc import Callable
from typing import override

from ......common.game.common import Trajectory
from ......players.manual.reader.input import BaseInputManualReader
from ....common import ConnectionsFeedback, ConnectionsGuess, ConnectionsInfo


class ConnectionsInputManualReader(
    BaseInputManualReader[str, ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback]
):
    @override
    def input_guess(
        self,
        *,
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        input_func: Callable[[str], str],
    ) -> ConnectionsGuess:
        turn_id: int = len(trajectory.turns) + 1
        indices: list[int] = []

        for i in range(4):
            guess: str = input_func(self.prompt_config.format(turn_id=turn_id, word_id=i + 1))
            indices.append(int(guess) if guess.isdigit() else -1)

        return ConnectionsGuess(indices=indices)
