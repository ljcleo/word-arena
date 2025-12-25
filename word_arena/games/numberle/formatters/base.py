from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleInGameFormatter(
    BaseInGameFormatter[NumberleInfo, None, NumberleGuess, NumberleFeedback]
):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: NumberleInfo) -> Iterator[str]:
        yield f"Number of Secret Equations: {game_info.num_targets}"
        yield f"Equation Length in Characters: {game_info.expr_len}"

        yield (
            "Maximum Number of Guesses: "
            f"{'Unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: NumberleInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: NumberleInfo, hint: None, guess: NumberleGuess
    ) -> Iterator[str]:
        yield f"Guess: {guess.equation}"

    @override
    @classmethod
    def format_feedback(
        cls,
        *,
        game_info: NumberleInfo,
        hint: None,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Feedback:",
                f"Accept | {'/'.join(feedback.patterns)}"
                if isinstance(feedback, NumberleResponse)
                else f"Reject | {feedback.error}",
            )
        )


class NumberleFinalResultFormatter(BaseFinalResultFormatter[NumberleFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: NumberleFinalResult) -> Iterator[str]:
        yield " ".join(
            (
                "Game Result:",
                "Victory"
                if len(final_result.found_indices) == len(final_result.answers)
                else "Failed",
            )
        )

        yield "\n".join(
            (
                " ".join(
                    (
                        "Found Equations:",
                        ", ".join(
                            final_result.answers[index] for index in final_result.found_indices
                        ),
                    )
                ),
                f"Secret Equations: {'/'.join(final_result.answers)}",
            )
        )
