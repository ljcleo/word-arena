from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import ContextoHintFeedback, ContextoHintGuess
from ..common import ContextoHintNote, ContextoHintNoteStateInterface


class ContextoHintLogAgentRenderer(
    BaseLogAgentRenderer[
        list[str], ContextoHintGuess, ContextoHintFeedback, list[str], ContextoHintNote
    ]
):
    @override
    def format_note(
        self, *, note_state: ContextoHintNoteStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy
