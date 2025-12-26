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
    def format_game_info(cls, *, game_info: int) -> Iterator[tuple[str, str]]:
        yield "Maximum Number of Guesses", "Unlimited" if game_info <= 0 else str(game_info)

    @override
    @classmethod
    def format_hint(cls, *, game_info: int, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: int, hint: None, guess: ContextoGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: int, hint: None, guess: ContextoGuess, feedback: ContextoFeedback
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, ContextoResponse):
            yield "Validation Result", "Accept"
            yield "Lemma Form", feedback.lemma
            yield "Position", str(feedback.distance + 1)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error


class ContextoFinalResultFormatter(BaseFinalResultFormatter[ContextoFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: ContextoFinalResult) -> Iterator[tuple[str, str]]:
        if final_result.best_pos == 0:
            yield "Game Result", "Victory"
        else:
            yield "Game Result", "Failed"
            yield "Best Guess", f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield "Secret Word", final_result.top_words[0]
        yield "Top 30 Words", ", ".join(final_result.top_words[:30])
