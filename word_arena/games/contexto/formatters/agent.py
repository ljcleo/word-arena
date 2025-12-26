from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    ContextoFeedback,
    ContextoFinalResult,
    ContextoGuess,
    ContextoNote,
)
from .base import ContextoFinalResultFormatter, ContextoInGameFormatter


class ContextoAgentCommonFormatter(
    BaseAgentCommonFormatter[int, None, ContextoGuess, ContextoFeedback, ContextoNote],
    ContextoInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: ContextoNote) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note.law
        yield "Possible Strategies", note.strategy


class ContextoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[int, None, ContextoGuess, ContextoFeedback, ContextoNote],
    ContextoAgentCommonFormatter,
):
    pass


class ContextoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote
    ],
    ContextoAgentCommonFormatter,
    ContextoFinalResultFormatter,
):
    pass
