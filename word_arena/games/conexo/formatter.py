from collections.abc import Iterator
from typing import override

from ...common.formatter.agent import BaseAgentFormatter
from ...common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ...common.memory.common import Turn
from .common import ConexoExperience, ConexoFeedback, ConexoFinalResult, ConexoInfo, ConexoWordGroup


class ConexoInGameFormatter(BaseInGameFormatter[ConexoInfo, None, set[int], ConexoFeedback]):
    @override
    @staticmethod
    def format_game_info(*, game_info: ConexoInfo) -> Iterator[str]:
        yield " ".join(
            (
                "Words:",
                "; ".join(f"{index + 1}. {word}" for index, word in enumerate(game_info.words)),
            )
        )

        yield f"Group Size: {game_info.group_size}"

        yield (
            "Maximum number of guesses: "
            f"{'unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @staticmethod
    def format_hint(*, game_info: ConexoInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @staticmethod
    def format_guess(*, game_info: ConexoInfo, hint: None, guess: set[int]) -> Iterator[str]:
        yield " ".join(
            (
                "Guess:",
                ", ".join(
                    game_info.words[index] if 0 <= index < len(game_info.words) else "(N/A)"
                    for index in guess
                ),
            )
        )

    @override
    @staticmethod
    def format_feedback(
        *, game_info: ConexoInfo, hint: None, guess: set[int], feedback: ConexoFeedback
    ) -> Iterator[str]:
        if feedback.accepted:
            yield " | ".join(
                (
                    "Feedback: Accept",
                    "Not in the Same Group"
                    if feedback.message is None
                    else f"In the Same Group; Theme: {feedback.message}",
                )
            )
        else:
            yield f"Feedback: Reject | {feedback.message}"


class ConexoFinalResultFormatter(BaseFinalResultFormatter[ConexoFinalResult]):
    @override
    @staticmethod
    def format_final_result(*, final_result: ConexoFinalResult) -> Iterator[str]:
        is_win: bool = len(final_result.remaining_groups) == 0
        yield f"Game Result: {'Victory' if is_win else 'Failed'}"

        yield ConexoFinalResultFormatter._format_groups(
            groups=final_result.found_groups, title="Found Groups"
        )

        if not is_win:
            yield ConexoFinalResultFormatter._format_groups(
                groups=final_result.remaining_groups, title="Groups Not Found"
            )

    @staticmethod
    def _format_groups(*, groups: list[ConexoWordGroup], title: str) -> str:
        return "\n".join(
            (
                f"{title}:",
                *(f"- {ConexoFinalResultFormatter._format_group(group=group)}" for group in groups),
            )
        )

    @staticmethod
    def _format_group(*, group: ConexoWordGroup) -> str:
        return " ".join((f"{group.theme}:", *group.words))


class ConexoAgentFormatter(
    BaseAgentFormatter[
        ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult, ConexoExperience
    ]
):
    @override
    @staticmethod
    def format_turn(
        *,
        game_info: ConexoInfo,
        turn: Turn[None, set[int], ConexoFeedback],
        final_result: ConexoFinalResult | None,
    ) -> Iterator[str]:
        yield from ConexoInGameFormatter.format_guess(
            game_info=game_info, hint=turn.hint, guess=turn.guess
        )

        yield from ConexoInGameFormatter.format_feedback(
            game_info=game_info, hint=turn.hint, guess=turn.guess, feedback=turn.feedback
        )

    @override
    @staticmethod
    def format_experience(*, experience: ConexoExperience) -> Iterator[str]:
        yield "Current Notes about Word Group Laws:"
        yield experience.law
        yield "Current Notes about Possible Strategies:"
        yield experience.strategy

    @override
    @staticmethod
    def get_in_game_formatter_cls() -> type[ConexoInGameFormatter]:
        return ConexoInGameFormatter

    @override
    @staticmethod
    def get_final_result_formatter_cls() -> type[ConexoFinalResultFormatter]:
        return ConexoFinalResultFormatter
