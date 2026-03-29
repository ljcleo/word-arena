from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from ..state import PlayerGameStateInterface, PlayerNoteStateInterface
from .base import BasePlayerRenderer


class BaseLogPlayerRenderer[PT, NT, IT, AT, GT, FT, RT, ST](
    BasePlayerRenderer[NT, IT, AT, GT, FT, RT, ST], ABC
):
    def __init__(self, *, player_log_func: Callable[[str, str], None], prompt_config: PT):
        self._player_log_func: Callable[[str, str], None] = player_log_func
        self._prompt_config: PT = prompt_config

    @property
    def prompt_config(self) -> PT:
        return self._prompt_config

    @override
    def render_note(
        self, *, note_state: PlayerNoteStateInterface[NT, IT, AT, GT, FT, RT, ST]
    ) -> None:
        self._log(*self.format_note(note=note_state.note))

    @override
    def render_last_analysis(
        self, *, game_state: PlayerGameStateInterface[IT, AT, GT, FT, RT]
    ) -> None:
        analysis: AT | None = game_state.last_analysis
        if analysis is not None:
            self._log(*self.format_analysis(analysis=analysis))

    @override
    def render_reflection(self, *, reflection: ST) -> None:
        self._log(*self.format_reflection(reflection=reflection))

    @abstractmethod
    def format_note(self, *, note: NT) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_analysis(self, *, analysis: AT) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_reflection(self, *, reflection: ST) -> Iterator[tuple[str, str]]: ...

    def _log(self, *output: tuple[str, str]) -> None:
        for key, value in output:
            self._player_log_func(key, value)
