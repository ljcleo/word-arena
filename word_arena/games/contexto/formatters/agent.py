from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    ContextoExperience,
    ContextoFeedback,
    ContextoFinalResult,
    ContextoGuess,
)
from .base import ContextoFinalResultFormatter, ContextoInGameFormatter


class ContextoAgentCommonFormatter(
    BaseAgentCommonFormatter[int, None, ContextoGuess, ContextoFeedback, ContextoExperience],
    ContextoInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: ContextoExperience) -> Iterator[str]:
        yield "Current Notes about Word Similarity Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class ContextoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[int, None, ContextoGuess, ContextoFeedback, ContextoExperience],
    ContextoAgentCommonFormatter,
):
    pass


class ContextoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoExperience
    ],
    ContextoAgentCommonFormatter,
    ContextoFinalResultFormatter,
):
    pass
