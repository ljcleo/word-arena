from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleInfoPrompterPromptConfig(BaseModel):
    num_targets: str
    eq_length: str
    max_turns: str
    unlimited: str


class NumberleGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class NumberleFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    invalid_guess: str


class NumberleFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_equations: str
    answers: str


class NumberleAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: NumberleInfoPrompterPromptConfig
    guess: NumberleGuessPrompterPromptConfig
    feedback: NumberleFeedbackPrompterPromptConfig
    final_result: NumberleFinalResultPrompterPromptConfig


class NumberleAgentPrompter(
    BaseAgentPrompter[
        NumberleAgentPrompterPromptConfig,
        NumberleInfo,
        NumberleGuess,
        NumberleFeedback,
        NumberleFinalResult,
    ]
):
    GUESS_CLS = NumberleGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback]
    ) -> NumberleGuess:
        return NumberleGuess(equation="5-4*3/2+1=0")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: NumberleInfo = trajectory.game_info
        prompt: NumberleInfoPrompterPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)
        yield prompt.eq_length, str(game_info.eq_length)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        turn_id: int,
        guess: NumberleGuess,
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess.guess, guess.equation

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        turn_id: int,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: NumberleFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, NumberleResponse):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback.patterns)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        final_result: NumberleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: NumberleFinalResultPrompterPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_equations,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
