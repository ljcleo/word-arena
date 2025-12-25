from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import (
    NumberleExperience,
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
)
from .base import NumberleFinalResultFormatter, NumberleInGameFormatter


class NumberleAgentCommonFormatter(
    BaseAgentCommonFormatter[
        NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleExperience
    ],
    NumberleInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: NumberleExperience) -> Iterator[str]:
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class NumberleAgentPlayerFormatter(
    BaseAgentPlayerFormatter[
        NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleExperience
    ],
    NumberleAgentCommonFormatter,
):
    pass


class NumberleAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleExperience
    ],
    NumberleAgentCommonFormatter,
    NumberleFinalResultFormatter,
):
    pass
