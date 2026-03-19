from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ..common import StrandsNote, StrandsNoteStateInterface


class StrandsLogAgentRenderer(
    BaseLogAgentRenderer[
        StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote
    ]
):
    @override
    def format_note(self, *, note_state: StrandsNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
