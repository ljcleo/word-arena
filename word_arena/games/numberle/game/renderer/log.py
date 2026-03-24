from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)
from ..state import NumberleGameStateInterface


class NumberleInfoPromptConfig(BaseModel):
    num_targets: str
    eq_length: str
    max_turns: str
    unlimited: str


class NumberleFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    invalid_guess: str


class NumberleFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_equations: str
    answers: str


class NumberleLogPromptConfig(BaseModel):
    game_info: NumberleInfoPromptConfig
    guess: str
    feedback: NumberleFeedbackPromptConfig
    final_result: NumberleFinalResultPromptConfig


class NumberleLogGameRenderer(
    BaseLogGameRenderer[
        NumberleLogPromptConfig, NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
    ]
):
    @override
    def format_game_info(self, *, state: NumberleGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: NumberleInfo = state.game_info
        prompt: NumberleInfoPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)
        yield prompt.eq_length, str(game_info.eq_length)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: NumberleGameStateInterface, guess: NumberleGuess
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.equation

    @override
    def format_last_feedback(
        self, *, state: NumberleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: NumberleFeedback = state.turns[-1].feedback
        prompt: NumberleFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, NumberleResponse):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback.patterns)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

    @override
    def format_final_result(
        self, *, state: NumberleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        final_result: NumberleFinalResult = state.final_result
        prompt: NumberleFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_equations,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
