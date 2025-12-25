from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
    LetrosoResponse,
)


class LetrosoInGameFormatter(BaseInGameFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: LetrosoInfo) -> Iterator[str]:
        yield f"Number of Secret Words: {game_info.num_targets}"
        yield f"Maximum Number of Letters in One Guess: {game_info.max_letters}"

        yield (
            "Maximum Number of Guesses: "
            f"{'Unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: LetrosoInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: LetrosoInfo, hint: None, guess: LetrosoGuess
    ) -> Iterator[str]:
        yield f"Guess: {guess.word}"

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: LetrosoInfo, hint: None, guess: LetrosoGuess, feedback: LetrosoFeedback
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Feedback:",
                f"Accept | {'/'.join(feedback.patterns)}"
                if isinstance(feedback, LetrosoResponse)
                else f"Reject | {feedback.error}",
            )
        )


class LetrosoFinalResultFormatter(BaseFinalResultFormatter[LetrosoFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: LetrosoFinalResult) -> Iterator[str]:
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
                        "Found Words:",
                        ", ".join(
                            final_result.answers[index] for index in final_result.found_indices
                        ),
                    )
                ),
                f"Secret Words: {'/'.join(final_result.answers)}",
            )
        )
