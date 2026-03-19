from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ..common import TuringNote, TuringNoteStateInterface


class TuringLogAgentRenderer(
    BaseLogAgentRenderer[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote]
):
    @override
    def format_note(self, *, note_state: TuringNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
