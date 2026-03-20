from collections.abc import Iterable, Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import (
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)
from ..state import RedactleGameStateInterface


class RedactleLogGameRenderer(
    BaseLogGameRenderer[RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult]
):
    @override
    def format_game_info(self, *, state: RedactleGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: RedactleInfo = state.game_info
        yield "Redacted Article", self._format_article(state=state, is_final=False)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: RedactleGameStateInterface, guess: RedactleGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def format_last_feedback(
        self, *, state: RedactleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: RedactleFeedback = state.turns[-1].feedback

        if isinstance(feedback, RedactleResponse):
            yield "Validation Result", "Accept"
            yield "Lemma", feedback.lemma

            yield (
                "Positions",
                self._format_items(
                    items=(
                        f"L{line_index}:{word_index}"
                        for line_index, word_index in feedback.positions
                    )
                ),
            )

            yield "Current Article", self._format_article(state=state, is_final=False)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    @override
    def format_final_result(
        self, *, state: RedactleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: RedactleFinalResult = state.final_result

        yield (
            "Game Result",
            "Victory"
            if len(final_result.found_words) == len(final_result.title_words)
            else "Failed",
        )

        yield ("Found Words", self._format_items(items=final_result.found_words))
        yield "Article Title", final_result.title
        yield ("Title Words", self._format_items(items=final_result.title_words))
        yield "Full Article", self._format_article(state=state, is_final=True)

    def _format_article(self, *, state: RedactleGameStateInterface, is_final: bool) -> str:
        return "\n".join(
            f"{line_index}: "
            + self._format_line(
                line=line,
                visible_words=None
                if is_final
                else state.game_info.stop_words
                | {
                    turn.feedback.lemma
                    for turn in state.turns
                    if isinstance(turn.feedback, RedactleResponse)
                },
            )
            for line_index, line in enumerate(state.game_info.article[:10])
        )

    def _format_line(
        self, *, line: list[tuple[str, str | None]], visible_words: set[str] | None
    ) -> str:
        return "".join(
            word
            if lemma is None or visible_words is None or lemma in visible_words
            else "█" * len(word)
            for word, lemma in line
        )

    def _format_items(self, *, items: Iterable[str]) -> str:
        result: str = ", ".join(items)
        return "N/A" if result == "" else result
