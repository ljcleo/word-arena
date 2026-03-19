from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..common import ContextoNote, ContextoNoteStateInterface


class ContextoLogAgentRenderer(
    BaseLogAgentRenderer[int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote]
):
    @override
    def format_note(self, *, note_state: ContextoNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy
