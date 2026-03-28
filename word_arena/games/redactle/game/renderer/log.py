from collections.abc import Iterator
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
    def format_game_info(self, *, game_info: RedactleInfo) -> Iterator[tuple[str, str]]:
        prompt: RedactleInfoPromptConfig = self.prompt_config.game_info

        yield (
            prompt.article,
            self._format_article(
                trajectory=Trajectory(game_info=game_info, turns=[]), is_final=False
            ),
        )

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

            yield prompt.article, self._format_article(trajectory=trajectory, is_final=False)
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
        prompt: RedactleFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_words) == len(final_result.title_words)],
        )

        yield prompt.found_words, join_or_na(final_result.found_words)
        yield prompt.title, final_result.title
        yield prompt.title_words, join_or_na(final_result.title_words)
        yield prompt.article, self._format_article(trajectory=trajectory, is_final=True)

    def _format_article(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        is_final: bool,
    ) -> str:
        visible_words: set[str] | None = (
            None
            if is_final
            else trajectory.game_info.stop_words
            | {
                turn.feedback.lemma
                for turn in trajectory.turns
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
            for line_index, line in enumerate(trajectory.game_info.article[:10])
        )
