from typing import Any, override

from ...common.player.base import BasePlayer
from .reader.base import BaseManualReader


class ManualPlayer[GT](BasePlayer[Any, GT, Any, Any]):
    def __init__(self, *, reader: BaseManualReader[GT]) -> None:
        self._reader: BaseManualReader[GT] = reader

    @override
    def prepare(self, *, game_info: Any) -> None:
        self._num_turns: int = 0

    @override
    def guess(self) -> GT:
        return self._reader.read_guess(turn_id=self._num_turns)

    @override
    def digest(self, *, guess: GT, feedback: Any) -> None:
        self._num_turns += 1

    @override
    def reflect(self, *, final_result: Any) -> None:
        pass

    @override
    def evolve(self) -> None:
        pass
