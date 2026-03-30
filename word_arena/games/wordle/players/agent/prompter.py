from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo


class WordleInfoPrompterPromptConfig(BaseModel):
    num_targets: str
    max_turns: str
    unlimited: str


class WordleGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class WordleFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class WordleFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    answers: str


class WordleAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: WordleInfoPrompterPromptConfig
    guess: WordleGuessPrompterPromptConfig
    feedback: WordleFeedbackPrompterPromptConfig
    final_result: WordleFinalResultPrompterPromptConfig


class WordleAgentPrompter(
    BaseAgentPrompter[
        WordleAgentPrompterPromptConfig, WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult
    ]
):
    GUESS_CLS = WordleGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback]
    ) -> WordleGuess:
        return WordleGuess(word="world")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: WordleInfo = trajectory.game_info
        prompt: WordleInfoPrompterPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        turn_id: int,
        guess: WordleGuess,
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess.guess, guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        turn_id: int,
        guess: WordleGuess,
        feedback: WordleFeedback,
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: WordleFeedbackPrompterPromptConfig = self.prompt_config.feedback

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
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        final_result: WordleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: WordleFinalResultPrompterPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_words,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
