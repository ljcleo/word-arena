from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import (
    LetrosoExperience,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoInfo,
    LetrosoResponse,
)


class LetrosoInGameFormatter(BaseInGameFormatter[LetrosoInfo, None, str, LetrosoFeedback]):
    @override
    @staticmethod
    def format_game_info(*, game_info: LetrosoInfo) -> Iterator[str]:
        yield f"Number of secret words: {game_info.num_targets}"
        yield f"Maximum number of letters in one guess: {game_info.max_letters}"

        yield (
            "Maximum number of guesses: "
            f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @staticmethod
    def format_hint(*, game_info: LetrosoInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_guess(*, game_info: LetrosoInfo, hint: None, guess: str) -> Iterator[str]:
        yield f"Guess: {guess}"

    @override
    @staticmethod
    def format_feedback(
        *, game_info: LetrosoInfo, hint: None, guess: str, feedback: LetrosoFeedback
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
    @staticmethod
    def format_final_result(*, final_result: LetrosoFinalResult) -> Iterator[str]:
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


class LetrosoAgentFormatter(
    BaseAgentFormatter[
        LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience
    ]
):
    @override
    @staticmethod
    def format_turn(
        *,
        game_info: LetrosoInfo,
        turn: Turn[None, str, LetrosoFeedback],
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[str]:
        yield from LetrosoInGameFormatter.format_guess(
            game_info=game_info, hint=turn.hint, guess=turn.guess
        )

        yield from LetrosoInGameFormatter.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @override
    @staticmethod
    def format_experience(*, experience: LetrosoExperience) -> Iterator[str]:
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy

    @override
    @staticmethod
    def get_in_game_formatter_cls() -> type[LetrosoInGameFormatter]:
        return LetrosoInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[LetrosoFinalResultFormatter]:
        return LetrosoFinalResultFormatter
