from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleInfoLogPromptConfig(BaseModel):
    num_targets: str
    eq_length: str
    max_turns: str
    unlimited: str


class NumberleFeedbackLogPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    invalid_guess: str


class NumberleFinalResultLogPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_equations: str
    answers: str


class NumberleLogPromptConfig(BaseModel):
    game_info: NumberleInfoLogPromptConfig
    guess: str
    feedback: NumberleFeedbackLogPromptConfig
    final_result: NumberleFinalResultLogPromptConfig


class NumberleLogGameRenderer(
    BaseLogGameRenderer[
        NumberleLogPromptConfig, NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: NumberleInfo) -> Iterator[tuple[str, str]]:
        prompt: NumberleInfoLogPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)
        yield prompt.eq_length, str(game_info.eq_length)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        guess: NumberleGuess,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.equation

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: NumberleFeedback = trajectory.turns[-1].feedback
        prompt: NumberleFeedbackLogPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, NumberleResponse):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback.patterns)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        final_result: NumberleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: NumberleFinalResultLogPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_equations,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
