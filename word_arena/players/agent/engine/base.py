from abc import ABC, abstractmethod

from ..common import AnalyzedGuess, GameSummary
from ..state import AgentGameStateInterface, AgentNoteStateInterface


class BaseAgentEngine[IT, GT, FT, RT, NT](ABC):
    @abstractmethod
    def create_note(self) -> NT: ...

    @abstractmethod
    def analyze_and_guess(
        self,
        *,
        note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT],
        game_state: AgentGameStateInterface[IT, GT, FT, RT],
    ) -> AnalyzedGuess[GT]: ...

    @abstractmethod
    def summarize_and_reflect(
        self,
        *,
        note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT],
        game_state: AgentGameStateInterface[IT, GT, FT, RT],
    ) -> GameSummary[IT, GT, FT, RT]: ...

    @abstractmethod
    def update_note(self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]) -> NT: ...
