from collections.abc import Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import ContextoHintFeedback, ContextoHintGuess
from ..state import ContextoHintGameStateInterface


class ContextoHintLogGameRenderer(
    BaseLogGameRenderer[list[str], ContextoHintGuess, ContextoHintFeedback, list[str]]
):
    @override
    def format_game_info(
        self, *, state: ContextoHintGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield self._format_choices(choices=state.game_info, is_first=True)

    @override
    def format_guess(
        self, *, state: ContextoHintGameStateInterface, guess: ContextoHintGuess
    ) -> Iterator[tuple[str, str]]:
        choices: list[str] | None = (
            state.game_info if len(state.turns) == 0 else state.turns[-1].feedback.next_choices
        )

        assert choices is not None
        yield (
            "Selected Word This Round",
            self._format_guess_index(choices=choices, index=guess.index),
        )

    @override
    def format_last_feedback(
        self, *, state: ContextoHintGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: ContextoHintFeedback = state.turns[-1].feedback

        if feedback.distance < 0:
            yield "Validation Result", "Reject"
            yield "Reason", "Invalid guess"
        else:
            yield "Validation Result", "Accept"
            yield "Position", str(feedback.distance + 1)

        if feedback.next_choices is not None:
            yield self._format_choices(choices=feedback.next_choices, is_first=False)

    @override
    def format_final_result(
        self, *, state: ContextoHintGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: list[str] = state.final_result
        yield "Secret Word", final_result[0]
        yield "Top 30 Words", ", ".join(final_result[:30])

    def _format_choices(self, *, choices: list[str], is_first: bool) -> tuple[str, str]:
        return f"Candidates for {'the First' if is_first else 'Next'} Round", "; ".join(
            f"{index}. {word}" for index, word in enumerate(choices)
        )

    def _format_guess_index(self, *, choices: list[str], index: int) -> str:
        return f"{index} ({choices[index] if 0 <= index < len(choices) else 'N/A'})"
