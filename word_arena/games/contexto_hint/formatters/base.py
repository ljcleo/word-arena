from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import ContextoHintGuess


class ContextoHintInGameFormatter(BaseInGameFormatter[None, list[str], ContextoHintGuess, int]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_hint(cls, *, game_info: None, hint: list[str]) -> Iterator[str]:
        yield " ".join(
            ("Options:", "; ".join(f"{index}. {word}" for index, word in enumerate(hint)))
        )

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: None, hint: list[str], guess: ContextoHintGuess
    ) -> Iterator[str]:
        yield " ".join(("Guess:", cls._format_guess_index(hint=hint, index=guess.index)))

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: None, hint: list[str], guess: ContextoHintGuess, feedback: int
    ) -> Iterator[str]:
        yield "Feedback: Invalid guess" if feedback < 0 else f"Feedback: Position {feedback + 1}"

    @classmethod
    def _format_guess_index(cls, *, hint: list[str], index: int) -> str:
        return f"{index} ({hint[index] if 0 <= index < len(hint) else 'N/A'})"


class ContextoHintFinalResultFormatter(BaseFinalResultFormatter[list[str]]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: list[str]) -> Iterator[str]:
        yield f"Secret Word: {final_result[0]}\nTop 30 Words: {', '.join(final_result[:30])}"
