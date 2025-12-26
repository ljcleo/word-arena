from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoNote
from .base import ConexoFinalResultFormatter, ConexoInGameFormatter


class ConexoAgentCommonFormatter(
    BaseAgentCommonFormatter[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoNote],
    ConexoInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: ConexoNote) -> Iterator[tuple[str, str]]:
        yield "Word Group Laws", note.law
        yield "Possible Strategies", note.strategy


class ConexoAgentPlayerFormatter(
    BaseAgentPlayerFormatter[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoNote],
    ConexoAgentCommonFormatter,
):
    pass


class ConexoAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote
    ],
    ConexoAgentCommonFormatter,
    ConexoFinalResultFormatter,
):
    pass
