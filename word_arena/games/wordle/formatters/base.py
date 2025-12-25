from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    WordleFeedback,
    WordleFinalResult,
    WordleGuess,
    WordleInfo,
    WordleResponse,
)


class WordleInGameFormatter(BaseInGameFormatter[WordleInfo, None, WordleGuess, WordleFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: WordleInfo) -> Iterator[str]:
        yield f"Number of Secret Words: {game_info.num_targets}"

        yield (
            "Maximum Number of Guesses: "
            f"{'Unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: WordleInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: WordleInfo, hint: None, guess: WordleGuess
    ) -> Iterator[str]:
        yield f"Guess: {guess.word}"

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: WordleInfo, hint: None, guess: WordleGuess, feedback: WordleFeedback
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Feedback:",
                f"Accept | {'/'.join(feedback.patterns)}"
                if isinstance(feedback, WordleResponse)
                else f"Reject | {feedback.error}",
            )
        )


class WordleFinalResultFormatter(BaseFinalResultFormatter[WordleFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: WordleFinalResult) -> Iterator[str]:
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
