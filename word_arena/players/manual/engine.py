from typing import Any, override

from ...common.player.common import AnalyzedGuess
from ...common.player.engine.base import BasePlayerEngine
from ...common.player.state import PlayerGameStateInterface, PlayerNoteStateInterface
from .reader.base import BaseManualReader


class ManualPlayerEngine[IT, GT, FT](BasePlayerEngine[None, IT, None, GT, FT, Any, None]):
    def __init__(self, *, reader: BaseManualReader[IT, GT, FT]) -> None:
        self._reader: BaseManualReader[IT, GT, FT] = reader

    @override
    def create_note(self) -> None: ...

    @override
    def analyze_and_guess(
        self,
        *,
        note_state: PlayerNoteStateInterface[None, IT, None, GT, FT, Any, None],
        game_state: PlayerGameStateInterface[IT, None, GT, FT, Any],
    ) -> AnalyzedGuess[None, GT]:
        return AnalyzedGuess(
            analysis=None, guess=self._reader.read_guess(trajectory=game_state.trajectory)
        )

    @override
    def summarize_and_reflect(
        self,
        *,
        note_state: PlayerNoteStateInterface[None, IT, None, GT, FT, Any, None],
        game_state: PlayerGameStateInterface[IT, None, GT, FT, Any],
    ) -> None: ...

    @override
    def update_note(
        self, *, note_state: PlayerNoteStateInterface[None, IT, None, GT, FT, Any, None]
    ) -> None: ...
