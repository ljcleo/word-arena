from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import (
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)


class RedactleInfoLogPromptConfig(BaseModel):
    article: str
    max_turns: str
    unlimited: str


class RedactleFeedbackLogPromptConfig(BaseModel):
    result: str
    accept: str
    lemma: str
    positions: str
    article: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class RedactleFinalResultLogPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    title: str
    title_words: str
    article: str


class RedactleLogPromptConfig(BaseModel):
    game_info: RedactleInfoLogPromptConfig
    guess: str
    feedback: RedactleFeedbackLogPromptConfig
    final_result: RedactleFinalResultLogPromptConfig


class RedactleLogGameRenderer(
    BaseLogGameRenderer[
        RedactleLogPromptConfig, RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: RedactleInfo) -> Iterator[tuple[str, str]]:
        prompt: RedactleInfoLogPromptConfig = self.prompt_config.game_info
        yield prompt.article, self._format_article(game_info=game_info, feedback_history=[])

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        guess: RedactleGuess,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.word

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: RedactleFeedback = trajectory.turns[-1].feedback
        prompt: RedactleFeedbackLogPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, RedactleResponse):
            yield prompt.result, prompt.accept
            yield prompt.lemma, feedback.lemma

            yield (
                prompt.positions,
                join_or_na(
                    f"L{line_index}:{word_index}" for line_index, word_index in feedback.positions
                ),
            )

            yield (
                prompt.article,
                self._format_article(
                    game_info=trajectory.game_info,
                    feedback_history=[turn.feedback for turn in trajectory.turns],
                ),
            )
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        final_result: RedactleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: RedactleFinalResultLogPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_words) == len(final_result.title_words)],
        )

        yield prompt.found_words, join_or_na(final_result.found_words)
        yield prompt.title, final_result.title
        yield prompt.title_words, join_or_na(final_result.title_words)

        yield (
            prompt.article,
            self._format_article(game_info=trajectory.game_info, feedback_history=None),
        )

    def _format_article(
        self, *, game_info: RedactleInfo, feedback_history: Iterable[RedactleFeedback] | None
    ) -> str:
        visible_words: set[str] | None = (
            None
            if feedback_history is None
            else game_info.stop_words
            | {
                feedback.lemma
                for feedback in feedback_history
                if isinstance(feedback, RedactleResponse)
            }
        )

        max_lines: int = 30

        lines: list[str] = [
            f"{line_index}: "
            + "".join(
                word
                if lemma is None or visible_words is None or lemma in visible_words
                else "█" * len(word)
                for word, lemma in line
            )
            for line_index, line in enumerate(game_info.article[:max_lines])
        ]

        if (trunc_lines := len(game_info.article) - max_lines) > 0:
            lines.append(f"({trunc_lines} lines truncated ...)")

        return "\n".join(lines)
