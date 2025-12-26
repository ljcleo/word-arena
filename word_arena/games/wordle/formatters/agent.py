from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleNote
from .base import WordleFinalResultFormatter, WordleInGameFormatter


class WordleAgentCommonFormatter(
    BaseAgentCommonFormatter[WordleInfo, None, WordleGuess, WordleFeedback, WordleNote],
    WordleInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: WordleNote) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note.strategy


class WordleAgentPlayerFormatter(
    BaseAgentPlayerFormatter[WordleInfo, None, WordleGuess, WordleFeedback, WordleNote],
    WordleAgentCommonFormatter,
):
    pass


class WordleAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote
    ],
    WordleAgentCommonFormatter,
    WordleFinalResultFormatter,
):
    pass
