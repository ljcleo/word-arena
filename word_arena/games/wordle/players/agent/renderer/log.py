from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..common import WordleNote, WordleNoteStateInterface


class WordleLogAgentRenderer(
    BaseLogAgentRenderer[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote]
):
    @override
    def format_note(self, *, note_state: WordleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy
