from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from ..common import Analysis, Reflection
from ..state import AgentGameStateInterface, AgentNoteStateInterface
from .base import BaseAgentRenderer


class BaseLogAgentRenderer[IT, GT, FT, RT, NT](BaseAgentRenderer[IT, GT, FT, RT, NT], ABC):
    def __init__(self, *, agent_log_func: Callable[[str, str], None]):
        self._agent_log_func: Callable[[str, str], None] = agent_log_func

    @override
    def render_note(self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]) -> None:
        self._log(*self.format_note(note_state=note_state))

    @override
    def render_last_analysis(self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self._format_analysis(analysis=game_state.last_analysis))

    @override
    def render_reflection(self, *, reflection: Reflection) -> None:
        self._log(*self._format_reflection(reflection=reflection))

    @abstractmethod
    def format_note(
        self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]
    ) -> Iterator[tuple[str, str]]: ...

    def _format_analysis(self, *, analysis: Analysis | None) -> Iterator[tuple[str, str]]:
        if analysis is not None:
            yield "Analysis", analysis.analysis
            yield "Plan", analysis.plan

    def _format_reflection(self, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        yield "Game Summary", reflection.summary
        yield "Reflection", reflection.reflection

    def _log(self, *output: tuple[str, str]):
        for key, value in output:
            self._agent_log_func(key, value)
