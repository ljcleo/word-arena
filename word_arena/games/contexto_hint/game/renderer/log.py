from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import ContextoHintFeedback, ContextoHintGuess


class ContextoHintFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    position: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ContextoHintFinalResultPromptConfig(BaseModel):
    secret_word: str
    top_words: str


class ContextoHintLogPromptConfig(BaseModel):
    choices: str
    guess: str
    feedback: ContextoHintFeedbackPromptConfig
    final_result: ContextoHintFinalResultPromptConfig


class ContextoHintLogGameRenderer(
    BaseLogGameRenderer[
        ContextoHintLogPromptConfig, list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
    ]
):
    @override
    def format_game_info(self, *, game_info: list[str]) -> Iterator[tuple[str, str]]:
        yield self._format_choices(turn_id=1, choices=game_info)

    @override
    def format_guess(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        guess: ContextoHintGuess,
    ) -> Iterator[tuple[str, str]]:
        choices: list[str] | None = (
            trajectory.game_info
            if len(trajectory.turns) == 0
            else trajectory.turns[-1].feedback.next_choices
        )

        assert choices is not None
        index: int = guess.index

        yield (
            self.prompt_config.guess,
            f"{index} ({choices[index] if 0 <= index < len(choices) else 'N/A'})",
        )

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: ContextoHintFeedback = trajectory.turns[-1].feedback
        prompt: ContextoHintFeedbackPromptConfig = self.prompt_config.feedback

        if feedback.distance >= 0:
            yield prompt.result, prompt.accept
            yield prompt.position, str(feedback.distance + 1)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

        if feedback.next_choices is not None:
            yield self._format_choices(
                turn_id=len(trajectory.turns) + 1, choices=feedback.next_choices
            )

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        final_result: list[str],
    ) -> Iterator[tuple[str, str]]:
        prompt: ContextoHintFinalResultPromptConfig = self.prompt_config.final_result
        yield prompt.secret_word, final_result[0]
        yield prompt.top_words, join_or_na(final_result[:30])

    def _format_choices(self, *, turn_id: int, choices: list[str]) -> tuple[str, str]:
        return self.prompt_config.choices.format(turn_id=turn_id), join_or_na(
            f"{index}. {word}" for index, word in enumerate(choices)
        )
