from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import ContextoHintGuess


class ContextoHintInGameFormatter(BaseInGameFormatter[None, list[str], ContextoHintGuess, int]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_hint(cls, *, game_info: None, hint: list[str]) -> Iterator[tuple[str, str]]:
        yield "Options", "; ".join(f"{index}. {word}" for index, word in enumerate(hint))

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: None, hint: list[str], guess: ContextoHintGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Selected Word", cls._format_guess_index(hint=hint, index=guess.index)

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: None, hint: list[str], guess: ContextoHintGuess, feedback: int
    ) -> Iterator[tuple[str, str]]:
        if feedback < 0:
            yield "Validation Result", "Reject"
            yield "Reason", "Invalid guess"
        else:
            yield "Validation Result", "Accept"
            yield "Position", str(feedback + 1)

    @classmethod
    def _format_guess_index(cls, *, hint: list[str], index: int) -> str:
        return f"{index} ({hint[index] if 0 <= index < len(hint) else 'N/A'})"


class ContextoHintFinalResultFormatter(BaseFinalResultFormatter[list[str]]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: list[str]) -> Iterator[tuple[str, str]]:
        yield "Secret Word", final_result[0]
        yield "Top 30 Words", ", ".join(final_result[:30])
