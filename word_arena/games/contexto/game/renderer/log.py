from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoResponse


class ContextoInfoPromptConfig(BaseModel):
    max_turns: str
    unlimited: str


class ContextoFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    lemma: str
    position: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ContextoFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    best_guess: str
    secret_word: str
    top_words: str


class ContextoLogPromptConfig(BaseModel):
    game_info: ContextoInfoPromptConfig
    guess: str
    feedback: ContextoFeedbackPromptConfig
    final_result: ContextoFinalResultPromptConfig


class ContextoLogGameRenderer(
    BaseLogGameRenderer[
        ContextoLogPromptConfig, int, ContextoGuess, ContextoFeedback, ContextoFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: int) -> Iterator[tuple[str, str]]:
        prompt: ContextoInfoPromptConfig = self.prompt_config.game_info
        yield prompt.max_turns, prompt.unlimited if game_info <= 0 else str(game_info)

    @override
    def format_guess(
        self, *, trajectory: Trajectory[int, ContextoGuess, ContextoFeedback], guess: ContextoGuess
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.word

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[int, ContextoGuess, ContextoFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: ContextoFeedback = trajectory.turns[-1].feedback
        prompt: ContextoFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, ContextoResponse):
            yield prompt.result, prompt.accept
            yield prompt.lemma, feedback.lemma
            yield prompt.position, str(feedback.distance + 1)
        else:
            yield prompt.result, prompt.reject

            yield (
                prompt.reject_reason,
                prompt.invalid_guess if feedback.error is None else feedback.error,
            )

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        final_result: ContextoFinalResult,
    ) -> Iterator[tuple[str, str]]:
        victory: bool = final_result.best_pos == 0
        prompt: ContextoFinalResultPromptConfig = self.prompt_config.final_result
        yield prompt.result, prompt.verdicts[victory]

        if not victory:
            yield prompt.best_guess, f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield prompt.secret_word, final_result.top_words[0]
        yield prompt.top_words, join_or_na(final_result.top_words[:30])
