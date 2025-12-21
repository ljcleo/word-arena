from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import ContextoHintExperience


class ContextoHintInGameFormatter(BaseInGameFormatter[None, list[str], int, int]):
    @override
    @staticmethod
    def format_game_info(*, game_info: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_hint(*, game_info: None, hint: list[str]) -> Iterator[str]:
        yield " ".join(
            (
                "Options (Use Index to Guess):",
                "; ".join(f"{index + 1}. {word}" for index, word in enumerate(hint)),
            )
        )

    @override
    @staticmethod
    def format_guess(*, game_info: None, hint: list[str], guess: int) -> Iterator[str]:
        yield f"Guess: {hint[guess] if 0 <= guess < len(hint) else '(N/A)'}"

    @override
    @staticmethod
    def format_feedback(
        *, game_info: None, hint: list[str], guess: int, feedback: int
    ) -> Iterator[str]:
        yield "Feedback: Invalid guess" if feedback < 0 else f"Feedback: Position {feedback + 1}"


class ContextoHintFinalResultFormatter(BaseFinalResultFormatter[list[str]]):
    @override
    @staticmethod
    def format_final_result(*, final_result: list[str]) -> Iterator[str]:
        yield f"Secret Word: {final_result[0]}\nTop 30 Words: {', '.join(final_result[:30])}"


class ContextoHintAgentFormatter(
    BaseAgentFormatter[None, list[str], int, int, list[str], ContextoHintExperience]
):
    @override
    @staticmethod
    def format_turn(
        *, game_info: None, turn: Turn[list[str], int, int], final_result: list[str] | None
    ) -> Iterator[str]:
        word_pos: dict[str, int] | None = (
            None
            if final_result is None
            else {word: pos + 1 for pos, word in enumerate(final_result)}
        )

        yield " ".join(
            (
                "Options:",
                ", ".join(turn.hint)
                if word_pos is None
                else ", ".join(f"{word} (Position: {word_pos[word]})" for word in turn.hint),
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
    def get_in_game_formatter_cls() -> type[BaseInGameFormatter[None, list[str], int, int]]:
        return ContextoHintInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[BaseFinalResultFormatter[list[str]]]:
        return ContextoHintFinalResultFormatter
