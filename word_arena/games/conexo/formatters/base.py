from collections.abc import Iterable, Iterator
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
    def format_game_info(cls, *, game_info: ConexoInfo) -> Iterator[tuple[str, str]]:
        yield "Words", "; ".join(f"{index}. {word}" for index, word in enumerate(game_info.words))
        yield "Group Size", str(game_info.group_size)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_guesses <= 0 else str(game_info.max_guesses),
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: ConexoInfo, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: ConexoInfo, hint: None, guess: ConexoGuess
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Selected Words",
            ", ".join(
                cls._format_guess_index(words=game_info.words, index=index)
                for index in guess.indices
            ),
        )

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: ConexoInfo, hint: None, guess: ConexoGuess, feedback: ConexoFeedback
    ) -> Iterator[tuple[str, str]]:
        if feedback.accepted:
            yield "Validation Result", "Accept"

            if feedback.message is None:
                yield "Is Same Group", "No"
            else:
                yield "Is Same Group", "Yes"
                yield "Theme", feedback.message
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "N/A" if feedback.message is None else feedback.message

    @classmethod
    def _format_guess_index(cls, *, words: list[str], index: int) -> str:
        return f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"


class ConexoFinalResultFormatter(BaseFinalResultFormatter[ConexoFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: ConexoFinalResult) -> Iterator[tuple[str, str]]:
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", cls._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield "Groups Not Found", cls._format_groups(groups=final_result.remaining_groups)

    @classmethod
    def _format_groups(cls, *, groups: Iterable[ConexoWordGroup]) -> str:
        result: str = "; ".join(f"{', '.join(group.words)} ({group.theme})" for group in groups)
        return "N/A" if result == "" else result
