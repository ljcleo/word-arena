from typing import Any, override

from ...common.game.common import Turn
from ...common.player.base import BasePlayer
from .reader.base import BaseManualReader
from .state import ManualGameState, ManualGameStateInterface


class ManualPlayer[IT, GT, FT](BasePlayer[IT, GT, FT, Any]):
    def __init__(self, *, reader: BaseManualReader[IT, GT, FT]) -> None:
        self._reader: BaseManualReader[IT, GT, FT] = reader
        self._game_state: ManualGameState[IT, GT, FT] = ManualGameState()

        self._ro_game_state: ManualGameStateInterface = ManualGameStateInterface(
            game_state=self._game_state
        )

    @property
    def game_state(self) -> ManualGameStateInterface[IT, GT, FT]:
        return self._ro_game_state

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._game_state.reset(game_info=game_info)

    @override
    def guess(self) -> GT:
        return self._reader.read_guess(game_state=self.game_state)

    @override
    def digest(self, *, guess: GT, feedback: FT) -> None:
        self._game_state.add_turn(turn=Turn(guess=guess, feedback=feedback))

    @override
    def reflect(self, *, final_result: Any) -> None: ...

    @override
    def evolve(self) -> None: ...
