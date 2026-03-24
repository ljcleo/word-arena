from collections.abc import Iterable, Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoWordGroup
from ..state import ConexoGameStateInterface


class ConexoLogGameRenderer(
    BaseLogGameRenderer[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult]
):
    @override
    def format_game_info(self, *, state: ConexoGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: ConexoInfo = state.game_info
        yield "Words", join_or_na(f"{index}. {word}" for index, word in enumerate(game_info.words))
        yield "Group Size", str(game_info.group_size)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: ConexoGameStateInterface, guess: ConexoGuess
    ) -> Iterator[tuple[str, str]]:
        words: list[str] = state.game_info.words

        yield (
            "Selected Words",
            join_or_na(
                f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"
                for index in guess.indices
            ),
        )

    @override
    def format_last_feedback(self, *, state: ConexoGameStateInterface) -> Iterator[tuple[str, str]]:
        feedback: ConexoFeedback = state.turns[-1].feedback
        message: str | None = feedback.message

        if feedback.accepted:
            yield "Validation Result", "Accept"

            if message is None:
                yield "Is Same Group", "No"
            else:
                yield "Is Same Group", "Yes"
                yield "Theme", message
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "N/A" if message is None else message

    @override
    def format_final_result(self, *, state: ConexoGameStateInterface) -> Iterator[tuple[str, str]]:
        final_result: ConexoFinalResult = state.final_result
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", self._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield ("Groups Not Found", self._format_groups(groups=final_result.remaining_groups))

    @classmethod
    def _format_groups(cls, *, groups: Iterable[ConexoWordGroup]) -> str:
        result: str = "; ".join(f"{join_or_na(group.words)} ({group.theme})" for group in groups)
        return "N/A" if result == "" else result
