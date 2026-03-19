from abc import ABC, abstractmethod

from ..common import Reflection
from ..state import AgentGameStateInterface, AgentNoteStateInterface


class BaseAgentRenderer[IT, GT, FT, RT, NT](ABC):
    @abstractmethod
    def render_note(self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]) -> None: ...

    @abstractmethod
    def render_last_analysis(
        self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]
    ) -> None: ...

    @abstractmethod
    def render_reflection(self, *, reflection: Reflection) -> None: ...
