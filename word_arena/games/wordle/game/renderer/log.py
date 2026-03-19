from collections.abc import Iterable, Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleResponse
from ..state import WordleGameStateInterface


class WordleLogGameRenderer(
    BaseLogGameRenderer[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]
):
    @override
    def format_game_info(self, *, state: WordleGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: WordleInfo = state.game_info
        yield "Number of Secret Words", str(game_info.num_targets)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: WordleGameStateInterface, guess: WordleGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def format_last_feedback(self, *, state: WordleGameStateInterface) -> Iterator[tuple[str, str]]:
        feedback: WordleFeedback = state.turns[-1].feedback

        if isinstance(feedback, WordleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    @override
    def format_final_result(self, *, state: WordleGameStateInterface) -> Iterator[tuple[str, str]]:
        final_result: WordleFinalResult = state.final_result

        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Words",
            self._format_found_words(
                words=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Words", "/".join(final_result.answers)

    def _format_found_words(self, *, words: Iterable[str]) -> str:
        result: str = ", ".join(words)
        return "N/A" if result == "" else result
