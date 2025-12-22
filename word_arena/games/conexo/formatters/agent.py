from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    ConexoExperience,
    ConexoFeedback,
    ConexoFinalResult,
    ConexoGuess,
    ConexoInfo,
)
from .base import ConexoFinalResultFormatter, ConexoInGameFormatter


class ConexoAgentCommonFormatter(
    BaseAgentCommonFormatter[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoExperience],
    ConexoInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: ConexoExperience) -> Iterator[str]:
        yield "Current Notes about Word Group Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class ConexoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoExperience],
    ConexoAgentCommonFormatter,
):
    pass


class ConexoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoExperience
    ],
    ConexoAgentCommonFormatter,
    ConexoFinalResultFormatter,
):
    pass
