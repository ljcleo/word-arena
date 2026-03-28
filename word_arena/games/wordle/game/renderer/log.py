from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleResponse


class WordleInfoPromptConfig(BaseModel):
    num_targets: str
    max_turns: str
    unlimited: str


class WordleFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    patterns: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class WordleFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    answers: str


class WordleLogPromptConfig(BaseModel):
    game_info: WordleInfoPromptConfig
    guess: str
    feedback: WordleFeedbackPromptConfig
    final_result: WordleFinalResultPromptConfig


class WordleLogGameRenderer(
    BaseLogGameRenderer[
        WordleLogPromptConfig, WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: WordleInfo) -> Iterator[tuple[str, str]]:
        prompt: WordleInfoPromptConfig = self.prompt_config.game_info
        yield prompt.num_targets, str(game_info.num_targets)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback], guess: WordleGuess
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess, guess.word

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: WordleFeedback = trajectory.turns[-1].feedback
        prompt: WordleFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, WordleResponse):
            yield prompt.result, prompt.accept
            yield prompt.patterns, join_or_na(feedback.patterns)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        final_result: WordleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: WordleFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
        )

        yield (
            prompt.found_words,
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield prompt.answers, join_or_na(final_result.answers)
