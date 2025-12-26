from collections.abc import Iterator
from typing import override

from ....common.formatter.agent import (
    BaseAgentCommonFormatter,
    BaseAgentMemoryFormatter,
    BaseAgentPlayerFormatter,
)
from ..common import ContextoHintGuess, ContextoHintNote
from .base import ContextoHintFinalResultFormatter, ContextoHintInGameFormatter


class ContextoHintAgentCommonFormatter(
    BaseAgentCommonFormatter[None, list[str], ContextoHintGuess, int, ContextoHintNote],
    ContextoHintInGameFormatter,
):
    @override
    @classmethod
    def format_note(cls, *, note: ContextoHintNote) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note.law
        yield "Possible Strategies", note.strategy


class ContextoHintAgentPlayerFormatter(
    BaseAgentPlayerFormatter[None, list[str], ContextoHintGuess, int, ContextoHintNote],
    ContextoHintAgentCommonFormatter,
):
    pass


class ContextoHintAgentMemoryFormatter(
    BaseAgentMemoryFormatter[None, list[str], ContextoHintGuess, int, list[str], ContextoHintNote],
    ContextoHintAgentCommonFormatter,
    ContextoHintFinalResultFormatter,
):
    @override
    @classmethod
    def format_hint_with_final_result(
        cls, *, game_info: None, hint: list[str], final_result: list[str]
    ) -> Iterator[tuple[str, str]]:
        word_pos: dict[str, int] = {word: pos + 1 for pos, word in enumerate(final_result)}

        yield (
            "Options",
            "; ".join(f"{index}. {word} ({word_pos[word]})" for index, word in enumerate(hint)),
        )
