from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import RedactleFeedback, RedactleFinalResult, RedactleInfo, RedactleGuess
from ..common import RedactleNote, RedactleNoteStateInterface


class RedactleLogAgentRenderer(
    BaseLogAgentRenderer[
        RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote
    ]
):
    @override
    def format_note(self, *, note_state: RedactleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
