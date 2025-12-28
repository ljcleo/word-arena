from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsNote,
)
from .base import ConnectionsFinalResultFormatter, ConnectionsInGameFormatter


class ConnectionsAgentCommonFormatter(
    BaseAgentCommonFormatter[
        ConnectionsInfo, None, ConnectionsGuess, ConnectionsFeedback, ConnectionsNote
    ],
    ConnectionsInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: ConnectionsNote) -> Iterator[tuple[str, str]]:
        yield "Word Group Laws", note.law
        yield "Possible Strategies", note.strategy


class ConnectionsAgentPlayerFormatter(
    BaseAgentPlayerFormatter[
        ConnectionsInfo, None, ConnectionsGuess, ConnectionsFeedback, ConnectionsNote
    ],
    ConnectionsAgentCommonFormatter,
):
    pass


class ConnectionsAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        ConnectionsInfo,
        None,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
    ],
    ConnectionsAgentCommonFormatter,
    ConnectionsFinalResultFormatter,
):
    pass
