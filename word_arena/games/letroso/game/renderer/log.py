from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo


class LetrosoInfoPromptConfig(BaseModel):
    num_targets: str
    max_letters: str
    max_turns: str
    unlimited: str


class LetrosoFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class LetrosoFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    answers: str


class LetrosoLogPromptConfig(BaseModel):
    game_info: LetrosoInfoPromptConfig
    guess: str
    feedback: LetrosoFeedbackPromptConfig
    final_result: LetrosoFinalResultPromptConfig


class LetrosoLogGameRenderer(
    BaseLogGameRenderer[
        LetrosoLogPromptConfig, LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: LetrosoInfo) -> Iterator[tuple[str, str]]:
        prompt: LetrosoInfoPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)
        yield prompt.max_letters, str(game_info.max_letters)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        guess: LetrosoGuess,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.word

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: LetrosoFeedback = trajectory.turns[-1].feedback
        prompt: LetrosoFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, list):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        final_result: LetrosoFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: LetrosoFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_words,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
