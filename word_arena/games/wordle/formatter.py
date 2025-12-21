from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import (
    WordleExperience,
    WordleFeedback,
    WordleFinalResult,
    WordleInfo,
    WordleResponse,
)


class WordleInGameFormatter(BaseInGameFormatter[WordleInfo, None, str, WordleFeedback]):
    @override
    @staticmethod
    def format_game_info(*, game_info: WordleInfo) -> Iterator[str]:
        yield f"Number of secret words: {game_info.num_targets}"

        yield (
            "Maximum number of guesses: "
            f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @staticmethod
    def format_hint(*, game_info: WordleInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_guess(*, game_info: WordleInfo, hint: None, guess: str) -> Iterator[str]:
        yield f"Guess: {guess}"

    @override
    @staticmethod
    def format_feedback(
        *, game_info: WordleInfo, hint: None, guess: str, feedback: WordleFeedback
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
    @staticmethod
    def format_final_result(*, final_result: WordleFinalResult) -> Iterator[str]:
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


class WordleAgentFormatter(
    BaseAgentFormatter[WordleInfo, None, str, WordleFeedback, WordleFinalResult, WordleExperience]
):
    @override
    @staticmethod
    def format_turn(
        *,
        game_info: WordleInfo,
        turn: Turn[None, str, WordleFeedback],
        final_result: WordleFinalResult | None,
    ) -> Iterator[str]:
        yield from WordleInGameFormatter.format_guess(
            game_info=game_info, hint=turn.hint, guess=turn.guess
        )

        yield from WordleInGameFormatter.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @override
    @staticmethod
    def format_experience(*, experience: WordleExperience) -> Iterator[str]:
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy

    @override
    @staticmethod
    def get_in_game_formatter_cls() -> type[WordleInGameFormatter]:
        return WordleInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[WordleFinalResultFormatter]:
        return WordleFinalResultFormatter
