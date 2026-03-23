from collections.abc import Callable, Iterator
from typing import override

from pydantic import BaseModel

from ..common import Analysis, Reflection
from ..state import AgentGameStateInterface, AgentNoteStateInterface
from .base import BaseAgentRenderer


class LogAgentRenderer[IT, GT, FT, RT, NT: BaseModel](BaseAgentRenderer[IT, GT, FT, RT, NT]):
    def __init__(self, *, agent_log_func: Callable[[str, str], None]):
        self._agent_log_func: Callable[[str, str], None] = agent_log_func

    @override
    def render_note(self, *, note_state: AgentNoteStateInterface[IT, GT, FT, RT, NT]) -> None:
        self._log(*self._format_model(data=note_state.note))

    @override
    def render_last_analysis(self, *, game_state: AgentGameStateInterface[IT, GT, FT, RT]) -> None:
        analysis: Analysis | None = game_state.last_analysis
        if analysis is not None:
            self._log(*self._format_model(data=analysis))

    @override
    def render_reflection(self, *, reflection: Reflection) -> None:
        self._log(*self._format_model(data=reflection))

    def _log(self, *output: tuple[str, str]) -> None:
        for key, value in output:
            self._agent_log_func(key, value)

    def _format_model(self, *, data: BaseModel) -> Iterator[tuple[str, str]]:
        for key, field in type(data).model_fields.items():
            yield str(field.title), str(getattr(data, key))
