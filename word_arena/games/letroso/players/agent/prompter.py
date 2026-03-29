from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo


class LetrosoInfoPrompterPromptConfig(BaseModel):
    num_targets: str
    max_letters: str
    max_turns: str
    unlimited: str


class LetrosoGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class LetrosoFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class LetrosoFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    answers: str


class LetrosoAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: LetrosoInfoPrompterPromptConfig
    guess: LetrosoGuessPrompterPromptConfig
    feedback: LetrosoFeedbackPrompterPromptConfig
    final_result: LetrosoFinalResultPrompterPromptConfig


class LetrosoAgentPrompter(
    BaseAgentPrompter[
        LetrosoAgentPrompterPromptConfig,
        LetrosoInfo,
        LetrosoGuess,
        LetrosoFeedback,
        LetrosoFinalResult,
    ]
):
    GUESS_CLS = LetrosoGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback]
    ) -> LetrosoGuess:
        return LetrosoGuess(word="feedback")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: LetrosoInfo = trajectory.game_info
        prompt: LetrosoInfoPrompterPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)
        yield prompt.max_letters, str(game_info.max_letters)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        turn_id: int,
        guess: LetrosoGuess,
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess.guess, guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        turn_id: int,
        guess: LetrosoGuess,
        feedback: LetrosoFeedback,
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: LetrosoFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, list):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        final_result: LetrosoFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: LetrosoFinalResultPrompterPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_words,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
