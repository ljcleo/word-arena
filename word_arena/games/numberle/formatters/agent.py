from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleNote,
)
from .base import NumberleFinalResultFormatter, NumberleInGameFormatter


class NumberleAgentCommonFormatter(
    BaseAgentCommonFormatter[NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleNote],
    NumberleInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: NumberleNote) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note.strategy


class NumberleAgentPlayerFormatter(
    BaseAgentPlayerFormatter[NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleNote],
    NumberleAgentCommonFormatter,
):
    pass


class NumberleAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote
    ],
    NumberleAgentCommonFormatter,
    NumberleFinalResultFormatter,
):
    pass
