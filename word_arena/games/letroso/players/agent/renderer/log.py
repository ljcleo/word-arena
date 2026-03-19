from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..common import LetrosoNote, LetrosoNoteStateInterface


class LetrosoLogAgentRenderer(
    BaseLogAgentRenderer[
        LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote
    ]
):
    @override
    def format_note(self, *, note_state: LetrosoNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
