from collections.abc import Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ..state import TuringGameStateInterface


class TuringLogGameRenderer(
    BaseLogGameRenderer[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]
):
    @override
    def format_game_info(self, *, state: TuringGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: TuringInfo = state.game_info
        for index, card in enumerate(game_info.verifiers):
            yield f"Verifier {index}", join_or_na(card)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: TuringGameStateInterface, guess: TuringGuess
    ) -> Iterator[tuple[str, str]]:
        if len(guess.verifiers) == 0:
            yield "Final Guess", str(guess.code)
        else:
            yield "Verifying Guess", str(guess.code)
            yield "Verifiers", join_or_na(map(str, guess.verifiers))

    @override
    def format_last_feedback(self, *, state: TuringGameStateInterface) -> Iterator[tuple[str, str]]:
        feedback: TuringFeedback = state.turns[-1].feedback

        if isinstance(feedback, list):
            yield "Validation Result", "Accept"
            yield "Verification Result", join_or_na("Y" if result else "N" for result in feedback)
        elif isinstance(feedback, bool):
            yield "Validation Result", "Accept"
            yield "Final Guess Result", "Correct" if feedback else "Incorrect"
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback

    @override
    def format_final_result(self, *, state: TuringGameStateInterface) -> Iterator[tuple[str, str]]:
        final_result: TuringFinalResult = state.final_result
        yield "Game Result", "Victory" if final_result.verdict is True else "Failed"
        yield "Asked Questions", str(final_result.num_questions)
        yield "Made Final Guess", "Yes" if final_result.verdict is not None else "No"
        yield "Secret Code", str(final_result.answer)
