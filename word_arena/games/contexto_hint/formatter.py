from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import ContextoHintExperience, ContextoHintGuess


class ContextoHintInGameFormatter(BaseInGameFormatter[None, list[str], ContextoHintGuess, int]):
    @override
    @staticmethod
    def format_game_info(*, game_info: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_hint(*, game_info: None, hint: list[str]) -> Iterator[str]:
        yield " ".join(
            ("Options:", "; ".join(f"{index}. {word}" for index, word in enumerate(hint)))
        )

    @override
    @staticmethod
    def format_guess(
        *, game_info: None, hint: list[str], guess: ContextoHintGuess
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Guess:",
                ContextoHintInGameFormatter._format_guess_index(hint=hint, index=guess.index),
            )
        )

    @override
    @staticmethod
    def format_feedback(
        *, game_info: None, hint: list[str], guess: ContextoHintGuess, feedback: int
    ) -> Iterator[str]:
        yield "Feedback: Invalid guess" if feedback < 0 else f"Feedback: Position {feedback + 1}"

    @staticmethod
    def _format_guess_index(*, hint: list[str], index: int) -> str:
        return f"{index} ({hint[index] if 0 <= index < len(hint) else 'N/A'})"


class ContextoHintFinalResultFormatter(BaseFinalResultFormatter[list[str]]):
    @override
    @staticmethod
    def format_final_result(*, final_result: list[str]) -> Iterator[str]:
        yield f"Secret Word: {final_result[0]}\nTop 30 Words: {', '.join(final_result[:30])}"


class ContextoHintAgentFormatter(
    BaseAgentFormatter[None, list[str], ContextoHintGuess, int, list[str], ContextoHintExperience]
):
    @override
    @staticmethod
    def format_turn(
        *,
        game_info: None,
        turn: Turn[list[str], ContextoHintGuess, int],
        final_result: list[str] | None,
    ) -> Iterator[str]:
        word_pos: dict[str, int] | None = (
            None
            if final_result is None
            else {word: pos + 1 for pos, word in enumerate(final_result)}
        )

        yield " ".join(
            (
                "Options:",
                "; ".join(
                    f"{index}. {word}"
                    if word_pos is None
                    else f"{index}. {word} (Position: {word_pos[word]})"
                    for index, word in enumerate(turn.hint)
                ),
            )
        )

        yield from ContextoHintInGameFormatter.format_guess(
            game_info=game_info, hint=turn.hint, guess=turn.guess
        )

        yield from ContextoHintInGameFormatter.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @override
    @staticmethod
    def format_experience(*, experience: ContextoHintExperience) -> Iterator[str]:
        yield "Current Notes about Word Similarity Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy

    @override
    @staticmethod
    def get_in_game_formatter_cls() -> type[ContextoHintInGameFormatter]:
        return ContextoHintInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[ContextoHintFinalResultFormatter]:
        return ContextoHintFinalResultFormatter
