from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import (
    ContextoExperience,
    ContextoFeedback,
    ContextoFinalResult,
    ContextoResponse,
    ContextoGuess,
)


class ContextoInGameFormatter(BaseInGameFormatter[int, None, ContextoGuess, ContextoFeedback]):
    @override
    @staticmethod
    def format_game_info(*, game_info: int) -> Iterator[str]:
        yield f"Maximum number of guesses: {'unlimited' if game_info <= 0 else game_info}"

    @override
    @staticmethod
    def format_hint(*, game_info: int, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_guess(*, game_info: int, hint: None, guess: ContextoGuess) -> Iterator[str]:
        yield f"Guess: {guess.word}"

    @override
    @staticmethod
    def format_feedback(
        *, game_info: int, hint: None, guess: ContextoGuess, feedback: ContextoFeedback
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Feedback:",
                f"Accept | Lemmatized as {feedback.lemma}; Position {feedback.distance + 1}"
                if isinstance(feedback, ContextoResponse)
                else f"Reject | {feedback.error}",
            )
        )


class ContextoFinalResultFormatter(BaseFinalResultFormatter[ContextoFinalResult]):
    @override
    @staticmethod
    def format_final_result(*, final_result: ContextoFinalResult) -> Iterator[str]:
        yield f"Game Result: {'Victory' if final_result.best_pos == 0 else 'Failed'}"
        yield f"Best Guess: {final_result.best_word} ({final_result.best_pos + 1})"

        yield "\n".join(
            (
                f"Secret Word: {final_result.top_words[0]}",
                f"Top 30 Words: {', '.join(final_result.top_words[:30])}",
            )
        )


class ContextoAgentFormatter(
    BaseAgentFormatter[
        int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoExperience
    ]
):
    @override
    @staticmethod
    def format_turn(
        *,
        game_info: int,
        turn: Turn[None, ContextoGuess, ContextoFeedback],
        final_result: ContextoFinalResult | None,
    ) -> Iterator[str]:
        yield from ContextoInGameFormatter.format_guess(
            game_info=game_info, hint=turn.hint, guess=turn.guess
        )

        yield from ContextoInGameFormatter.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @override
    @staticmethod
    def format_experience(*, experience: ContextoExperience) -> Iterator[str]:
        yield "Current Notes about Word Similarity Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy

    @override
    @staticmethod
    def get_in_game_formatter_cls() -> type[ContextoInGameFormatter]:
        return ContextoInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[ContextoFinalResultFormatter]:
        return ContextoFinalResultFormatter
