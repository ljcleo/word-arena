from abc import ABC, abstractmethod

from ..common import AnalyzedGuess
from ..state import PlayerGameStateInterface, PlayerNoteStateInterface


class BasePlayerEngine[NT, IT, AT, GT, FT, RT, ST](ABC):
    @abstractmethod
    def create_note(self) -> NT: ...

    @abstractmethod
    def analyze_and_guess(
        self,
        *,
        note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST],
        game_state: PlayerGameStateInterface[IT, AT, GT, FT, RT],
    ) -> AnalyzedGuess[AT, GT]: ...

    @abstractmethod
    def summarize_and_reflect(
        self,
        *,
        note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST],
        game_state: PlayerGameStateInterface[IT, AT, GT, FT, RT],
    ) -> ST: ...

    @abstractmethod
    def update_note(
        self, *, note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST]
    ) -> NT: ...
