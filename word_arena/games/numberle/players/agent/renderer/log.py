from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo
from ..common import NumberleNote, NumberleNoteStateInterface


class NumberleLogAgentRenderer(
    BaseLogAgentRenderer[
        NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote
    ]
):
    @override
    def format_note(self, *, note_state: NumberleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
