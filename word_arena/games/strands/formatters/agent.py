from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo, StrandsNote
from .base import StrandsFinalResultFormatter, StrandsInGameFormatter


class StrandsAgentCommonFormatter(
    BaseAgentCommonFormatter[StrandsInfo, None, StrandsGuess, StrandsFeedback, StrandsNote],
    StrandsInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: StrandsNote) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note.strategy


class StrandsAgentPlayerFormatter(
    BaseAgentPlayerFormatter[StrandsInfo, None, StrandsGuess, StrandsFeedback, StrandsNote],
    StrandsAgentCommonFormatter,
):
    pass


class StrandsAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        StrandsInfo, None, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote
    ],
    StrandsAgentCommonFormatter,
    StrandsFinalResultFormatter,
):
    pass
