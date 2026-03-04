from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    TuringFeedback,
    TuringFinalResult,
    TuringGuess,
    TuringInfo,
    TuringNote,
)
from .base import TuringFinalResultFormatter, TuringInGameFormatter


class TuringAgentCommonFormatter(
    BaseAgentCommonFormatter[TuringInfo, None, TuringGuess, TuringFeedback, TuringNote],
    TuringInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: TuringNote) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note.strategy


class TuringAgentPlayerFormatter(
    BaseAgentPlayerFormatter[TuringInfo, None, TuringGuess, TuringFeedback, TuringNote],
    TuringAgentCommonFormatter,
):
    pass


class TuringAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        TuringInfo, None, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote
    ],
    TuringAgentCommonFormatter,
    TuringFinalResultFormatter,
):
    pass
