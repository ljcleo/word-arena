from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..common import ConexoNote, ConexoNoteStateInterface


class ConexoLogAgentRenderer(
    BaseLogAgentRenderer[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote]
):
    @override
    def format_note(self, *, note_state: ConexoNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Word Group Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy
