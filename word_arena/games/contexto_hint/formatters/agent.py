from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import ContextoHintExperience, ContextoHintGuess
from .base import ContextoHintFinalResultFormatter, ContextoHintInGameFormatter


class ContextoHintAgentCommonFormatter(
    BaseAgentCommonFormatter[None, list[str], ContextoHintGuess, int, ContextoHintExperience],
    ContextoHintInGameFormatter,
):
    @override
    @classmethod
    def format_experience(cls, *, experience: ContextoHintExperience) -> Iterator[str]:
        yield "Current Notes about Word Similarity Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy


class ContextoHintAgentPlayerFormatter(
    BaseAgentPlayerFormatter[None, list[str], ContextoHintGuess, int, ContextoHintExperience],
    ContextoHintAgentCommonFormatter,
):
    pass


class ContextoHintAgentMemoryFormatter(
    BaseAgentMemoryFormatter[
        None, list[str], ContextoHintGuess, int, list[str], ContextoHintExperience
    ],
    ContextoHintAgentCommonFormatter,
    ContextoHintFinalResultFormatter,
):
    @override
    @classmethod
    def format_hint_with_final_result(
        cls, *, game_info: None, hint: list[str], final_result: list[str]
    ) -> Iterator[str]:
        word_pos: dict[str, int] = {word: pos + 1 for pos, word in enumerate(final_result)}

        yield " ".join(
            (
                "Options:",
                "; ".join(
                    f"{index}. {word} (Position: {word_pos[word]})"
                    for index, word in enumerate(hint)
                ),
            )
        )
