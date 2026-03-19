from typing import override

from ...common.player.base import BasePlayer
from .reader.base import BaseManualReader


class ManualPlayer[IT, GT, FT, RT](BasePlayer[IT, GT, FT, RT]):
    def __init__(self, *, reader: BaseManualReader[GT]) -> None:
        self._reader: BaseManualReader[GT] = reader

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._num_turns: int = 0

    @override
    def guess(self) -> GT:
        return self._reader.read_guess(turn_id=self._num_turns)

    @override
    def digest(self, *, guess: GT, feedback: FT) -> None:
        self._num_turns += 1

    @override
    def reflect(self, *, final_result: RT) -> None:
        pass

    @override
    def evolve(self) -> None:
        pass
