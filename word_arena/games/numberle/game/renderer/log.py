from collections.abc import Iterable, Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)
from ..common import NumberleGameStateInterface


class NumberleLogGameRenderer(
    BaseLogGameRenderer[NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult]
):
    @override
    def format_game_info(self, *, state: NumberleGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: NumberleInfo = state.game_info
        yield "Number of Secret Equations", str(game_info.num_targets)
        yield "Equation Length in Characters", str(game_info.eq_length)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: NumberleGameStateInterface, guess: NumberleGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Equation", guess.equation

    @override
    def format_last_feedback(
        self, *, state: NumberleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: NumberleFeedback = state.turns[-1].feedback

        if isinstance(feedback, NumberleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    @override
    def format_final_result(
        self, *, state: NumberleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: NumberleFinalResult = state.final_result

        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Equations",
            self._format_found_eqs(
                eqs=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Equations", "/".join(final_result.answers)

    def _format_found_eqs(self, *, eqs: Iterable[str]) -> str:
        result: str = ", ".join(eqs)
        return "N/A" if result == "" else result
