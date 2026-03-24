from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import (
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)
from ..state import RedactleGameStateInterface


class RedactleInfoPromptConfig(BaseModel):
    article: str
    max_turns: str
    unlimited: str


class RedactleFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    lemma: str
    positions: str
    article: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class RedactleFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    title: str
    title_words: str
    article: str


class RedactleLogPromptConfig(BaseModel):
    game_info: RedactleInfoPromptConfig
    guess: str
    feedback: RedactleFeedbackPromptConfig
    final_result: RedactleFinalResultPromptConfig


class RedactleLogGameRenderer(
    BaseLogGameRenderer[
        RedactleLogPromptConfig, RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
    ]
):
    @override
    def format_game_info(self, *, state: RedactleGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: RedactleInfo = state.game_info
        prompt: RedactleInfoPromptConfig = self.prompt_config.game_info
        yield prompt.article, self._format_article(state=state, is_final=False)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: RedactleGameStateInterface, guess: RedactleGuess
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.word

    @override
    def format_last_feedback(
        self, *, state: RedactleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: RedactleFeedback = state.turns[-1].feedback
        prompt: RedactleFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, RedactleResponse):
            yield prompt.result, prompt.accept
            yield prompt.lemma, feedback.lemma

            yield (
                prompt.positions,
                join_or_na(
                    f"L{line_index}:{word_index}" for line_index, word_index in feedback.positions
                ),
            )

            yield prompt.article, self._format_article(state=state, is_final=False)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def format_final_result(
        self, *, state: RedactleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: RedactleFinalResult = state.final_result
        prompt: RedactleFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_words) == len(final_result.title_words)],
        )

        yield prompt.found_words, join_or_na(final_result.found_words)
        yield prompt.title, final_result.title
        yield prompt.title_words, join_or_na(final_result.title_words)
        yield prompt.article, self._format_article(state=state, is_final=True)

    def _format_article(self, *, state: RedactleGameStateInterface, is_final: bool) -> str:
        visible_words: set[str] | None = (
            None
            if is_final
            else state.game_info.stop_words
            | {
                turn.feedback.lemma
                for turn in state.turns
                if isinstance(turn.feedback, RedactleResponse)
            }
        )

        return "\n".join(
            f"{line_index}: "
            + "".join(
                word
                if lemma is None or visible_words is None or lemma in visible_words
                else "█" * len(word)
                for word, lemma in line
            )
            for line_index, line in enumerate(state.game_info.article[:10])
        )
