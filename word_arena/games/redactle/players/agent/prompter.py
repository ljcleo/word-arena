from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import (
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)


class RedactleInfoPrompterPromptConfig(BaseModel):
    article: str
    max_turns: str
    unlimited: str


class RedactleGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class RedactleFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    lemma: str
    positions: str
    article: str
    reject: str
    reject_reason: str
    reject_messages: tuple[str, str]


class RedactleFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_words: str
    title: str
    title_words: str
    article: str


class RedactleAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: RedactleInfoPrompterPromptConfig
    guess: RedactleGuessPrompterPromptConfig
    feedback: RedactleFeedbackPrompterPromptConfig
    final_result: RedactleFinalResultPrompterPromptConfig


class RedactleAgentPrompter(
    BaseAgentPrompter[
        RedactleAgentPrompterPromptConfig,
        RedactleInfo,
        RedactleGuess,
        RedactleFeedback,
        RedactleFinalResult,
    ]
):
    GUESS_CLS = RedactleGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback]
    ) -> str:
        return self.prompt_config.guess.guess_detail

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback]
    ) -> RedactleGuess:
        return RedactleGuess(word="history")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: RedactleInfo = trajectory.game_info
        prompt: RedactleInfoPrompterPromptConfig = self.prompt_config.game_info

        if final_result is None:
            yield (
                prompt.article,
                self._format_article(
                    game_info=game_info,
                    feedback_history=[turn.feedback for turn in trajectory.turns],
                ),
            )

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        turn_id: int,
        guess: RedactleGuess,
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield self.prompt_config.guess.guess, guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        turn_id: int,
        guess: RedactleGuess,
        feedback: RedactleFeedback,
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: RedactleFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, RedactleResponse):
            yield prompt.result, prompt.accept
            yield prompt.lemma, feedback.lemma

            yield (
                prompt.positions,
                join_or_na(
                    f"L{line_index}:{word_index}" for line_index, word_index in feedback.positions
                ),
            )
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        final_result: RedactleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: RedactleFinalResultPrompterPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_words) == len(final_result.title_words)],
        )

        yield prompt.found_words, join_or_na(final_result.found_words)
        yield prompt.title, final_result.title
        yield prompt.title_words, join_or_na(final_result.title_words)

        yield (
            prompt.article,
            self._format_article(game_info=trajectory.game_info, feedback_history=None),
        )

    def _format_article(
        self, *, game_info: RedactleInfo, feedback_history: Iterable[RedactleFeedback] | None
    ) -> str:
        visible_words: set[str] | None = (
            None
            if feedback_history is None
            else game_info.stop_words
            | {
                feedback.lemma
                for feedback in feedback_history
                if isinstance(feedback, RedactleResponse)
            }
        )

        return "\n".join(
            f"{line_index}: "
            + "".join(
                word
                if lemma is None or visible_words is None or lemma in visible_words
                else "█" * len(word)
                for word, lemma in line
            )
            for line_index, line in enumerate(game_info.article)
        )
