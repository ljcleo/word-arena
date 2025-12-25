from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    ConexoFeedback,
    ConexoFinalResult,
    ConexoGuess,
    ConexoInfo,
    ConexoWordGroup,
)


class ConexoInGameFormatter(BaseInGameFormatter[ConexoInfo, None, ConexoGuess, ConexoFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: ConexoInfo) -> Iterator[str]:
        yield " ".join(
            ("Words:", "; ".join(f"{index}. {word}" for index, word in enumerate(game_info.words)))
        )

        yield f"Group Size: {game_info.group_size}"

        yield (
            "Maximum Number of Guesses: "
            f"{'Unlimited' if game_info.max_guesses <= 0 else game_info.max_guesses}"
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: ConexoInfo, hint: None) -> Iterator[str]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: ConexoInfo, hint: None, guess: ConexoGuess
    ) -> Iterator[str]:
        yield " ".join(
            (
                "Guess:",
                ", ".join(
                    cls._format_guess_index(words=game_info.words, index=index)
                    for index in guess.indices
                ),
            )
        )

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: ConexoInfo, hint: None, guess: ConexoGuess, feedback: ConexoFeedback
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

    @classmethod
    def _format_guess_index(cls, *, words: list[str], index: int) -> str:
        return f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"


class ConexoFinalResultFormatter(BaseFinalResultFormatter[ConexoFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: ConexoFinalResult) -> Iterator[str]:
        is_win: bool = len(final_result.remaining_groups) == 0
        yield f"Game Result: {'Victory' if is_win else 'Failed'}"

        yield cls._format_groups(groups=final_result.found_groups, title="Found Groups")

        if not is_win:
            yield cls._format_groups(groups=final_result.remaining_groups, title="Groups Not Found")

    @classmethod
    def _format_groups(cls, *, groups: list[ConexoWordGroup], title: str) -> str:
        return "\n".join(
            (f"{title}:", *(f"- {cls._format_group(group=group)}" for group in groups))
        )

    @classmethod
    def _format_group(cls, *, group: ConexoWordGroup) -> str:
        return f"{group.theme}: {', '.join(group.words)}"
