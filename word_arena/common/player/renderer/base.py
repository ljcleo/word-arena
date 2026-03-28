from abc import ABC, abstractmethod

from ..state import PlayerGameStateInterface, PlayerNoteStateInterface


class BasePlayerRenderer[NT, IT, AT, GT, FT, RT, ST](ABC):
    @abstractmethod
    def render_note(
        self, *, note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST]
    ) -> None: ...

    @abstractmethod
    def render_last_analysis(
        self, *, game_state: PlayerGameStateInterface[IT, AT, GT, FT, RT]
    ) -> None: ...

    @abstractmethod
    def render_reflection(self, *, reflection: ST) -> None: ...
