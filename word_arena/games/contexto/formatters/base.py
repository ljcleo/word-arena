from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    ContextoFeedback,
    ContextoFinalResult,
    ContextoGuess,
    ContextoResponse,
)


class ContextoInGameFormatter(BaseInGameFormatter[int, None, ContextoGuess, ContextoFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: int) -> Iterator[str]:
        yield f"Maximum number of guesses: {'unlimited' if game_info <= 0 else game_info}"

    @override
    @classmethod
    def format_hint(cls, *, game_info: int, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_guess(cls, *, game_info: int, hint: None, guess: ContextoGuess) -> Iterator[str]:
        yield f"Guess: {guess.word}"

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: int, hint: None, guess: ContextoGuess, feedback: ContextoFeedback
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
    @classmethod
    def format_final_result(cls, *, final_result: ContextoFinalResult) -> Iterator[str]:
        yield f"Game Result: {'Victory' if final_result.best_pos == 0 else 'Failed'}"
        yield f"Best Guess: {final_result.best_word} ({final_result.best_pos + 1})"

        yield "\n".join(
            (
                f"Secret Word: {final_result.top_words[0]}",
                f"Top 30 Words: {', '.join(final_result.top_words[:30])}",
            )
        )
