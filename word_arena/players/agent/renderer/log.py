from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from ....common.player.renderer.log import BaseLogPlayerRenderer
from ..common import Analysis, Reflection
from ..utils import format_model


class AgentLogPlayerRenderer[IT, GT, FT, RT, NT: BaseModel](
    BaseLogPlayerRenderer[NT, IT, Analysis, GT, FT, RT, Reflection]
):
    @override
    def format_note(self, *, note: NT) -> Iterator[tuple[str, str]]:
        yield from format_model(note)

    @override
    def format_analysis(self, *, analysis: Analysis) -> Iterator[tuple[str, str]]:
        yield from format_model(analysis)

    @override
    def format_reflection(self, *, reflection: Reflection) -> Iterator[tuple[str, str]]:
        yield from format_model(reflection)
