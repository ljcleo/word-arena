from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoResponse


class ContextoInfoPrompterPromptConfig(BaseModel):
    max_turns: str
    unlimited: str


class ContextoGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class ContextoFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    lemma: str
    position: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ContextoFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    best_guess: str
    secret_word: str
    top_words: str


class ContextoAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: ContextoInfoPrompterPromptConfig
    guess: ContextoGuessPrompterPromptConfig
    feedback: ContextoFeedbackPrompterPromptConfig
    final_result: ContextoFinalResultPrompterPromptConfig


class ContextoAgentPrompter(
    BaseAgentPrompter[
        ContextoAgentPrompterPromptConfig, int, ContextoGuess, ContextoFeedback, ContextoFinalResult
    ]
):
    GUESS_CLS = ContextoGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[int, ContextoGuess, ContextoFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[int, ContextoGuess, ContextoFeedback]
    ) -> ContextoGuess:
        return ContextoGuess(word="play")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: int = trajectory.game_info
        prompt: ContextoInfoPrompterPromptConfig = self.prompt_config.game_info
        yield prompt.max_turns, prompt.unlimited if game_info <= 0 else str(game_info)

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        turn_id: int,
        guess: ContextoGuess,
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess.guess, guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        turn_id: int,
        guess: ContextoGuess,
        feedback: ContextoFeedback,
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: ContextoFeedbackPrompterPromptConfig = self.prompt_config.feedback

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
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        final_result: ContextoFinalResult,
    ) -> Iterator[tuple[str, str]]:
        victory: bool = final_result.best_pos == 0
        prompt: ContextoFinalResultPrompterPromptConfig = self.prompt_config.final_result
        yield prompt.result, prompt.verdicts[victory]

        if not victory:
            yield prompt.best_guess, f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield prompt.secret_word, final_result.top_words[0]
        yield prompt.top_words, join_or_na(final_result.top_words[:30])
