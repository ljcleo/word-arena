from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo, LetrosoNote
from .base import LetrosoFinalResultFormatter, LetrosoInGameFormatter


class LetrosoAgentCommonFormatter(
    BaseAgentCommonFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoNote],
    LetrosoInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: LetrosoNote) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note.strategy


class LetrosoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoNote],
    LetrosoAgentCommonFormatter,
):
    pass


class LetrosoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote
    ],
    LetrosoAgentCommonFormatter,
    LetrosoFinalResultFormatter,
):
    pass
