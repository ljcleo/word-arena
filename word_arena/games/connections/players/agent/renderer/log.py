from collections.abc import Iterator
from typing import override

from ......players.agent.renderer.log import BaseLogAgentRenderer
from ....common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
)
from ..common import ConnectionsNote, ConnectionsNoteStateInterface


class ConnectionsLogAgentRenderer(
    BaseLogAgentRenderer[
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
    ]
):
    @override
    def format_note(
        self, *, note_state: ConnectionsNoteStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield "Word Group Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy
