from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    LetrosoExperience,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
)
from .base import LetrosoFinalResultFormatter, LetrosoInGameFormatter


class LetrosoAgentCommonFormatter(
    BaseAgentCommonFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoExperience],
    LetrosoInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: LetrosoExperience) -> Iterator[str]:
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class LetrosoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoExperience],
    LetrosoAgentCommonFormatter,
):
    pass


class LetrosoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience
    ],
    LetrosoAgentCommonFormatter,
    LetrosoFinalResultFormatter,
):
    pass
