from collections.abc import Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoResponse
from ..state import ContextoGameStateInterface


class ContextoLogGameRenderer(
    BaseLogGameRenderer[int, ContextoGuess, ContextoFeedback, ContextoFinalResult]
):
    @override
    def format_game_info(self, *, state: ContextoGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: int = state.game_info
        yield "Maximum Number of Guesses", "Unlimited" if game_info <= 0 else str(game_info)

    @override
    def format_guess(
        self, *, state: ContextoGameStateInterface, guess: ContextoGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def format_last_feedback(
        self, *, state: ContextoGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: ContextoFeedback = state.turns[-1].feedback

        if isinstance(feedback, ContextoResponse):
            yield "Validation Result", "Accept"
            yield "Lemma Form", feedback.lemma
            yield "Position", str(feedback.distance + 1)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    @override
    def format_final_result(
        self, *, state: ContextoGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: ContextoFinalResult = state.final_result

        if final_result.best_pos == 0:
            yield "Game Result", "Victory"
        else:
            yield "Game Result", "Failed"
            yield "Best Guess", f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield "Secret Word", final_result.top_words[0]
        yield "Top 30 Words", ", ".join(final_result.top_words[:30])
