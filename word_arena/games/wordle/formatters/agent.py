from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    WordleExperience,
    WordleFeedback,
    WordleFinalResult,
    WordleGuess,
    WordleInfo,
)
from .base import WordleFinalResultFormatter, WordleInGameFormatter


class WordleAgentCommonFormatter(
    BaseAgentCommonFormatter[WordleInfo, None, WordleGuess, WordleFeedback, WordleExperience],
    WordleInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: WordleExperience) -> Iterator[str]:
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class WordleAgentPlayerFormatter(
    BaseAgentPlayerFormatter[WordleInfo, None, WordleGuess, WordleFeedback, WordleExperience],
    WordleAgentCommonFormatter,
):
    pass


class WordleAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, WordleExperience
    ],
    WordleAgentCommonFormatter,
    WordleFinalResultFormatter,
):
    pass
