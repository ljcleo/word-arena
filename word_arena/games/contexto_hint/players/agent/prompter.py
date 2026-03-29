from collections.abc import Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import ContextoHintFeedback, ContextoHintGuess


class ContextoHintFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    position: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ContextoHintFinalResultPrompterPromptConfig(BaseModel):
    secret_word: str
    top_words: str


class ContextoHintGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class ContextoHintAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    choices: str
    guess: ContextoHintGuessPrompterPromptConfig
    feedback: ContextoHintFeedbackPrompterPromptConfig
    final_result: ContextoHintFinalResultPrompterPromptConfig


class ContextoHintAgentPrompter(
    BaseAgentPrompter[
        ContextoHintAgentPrompterPromptConfig,
        list[str],
        ContextoHintGuess,
        ContextoHintFeedback,
        list[str],
    ]
):
    GUESS_CLS = ContextoHintGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback]
    ) -> str:
        choices: list[str] | None = (
            trajectory.game_info
            if len(trajectory.turns) == 0
            else trajectory.turns[-1].feedback.next_choices
        )

        assert choices is not None
        example: int = len(choices) - 1

        return self.prompt_config.guess.guess_detail.format(
            example=example, choice=choices[example]
        )

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback]
    ) -> ContextoHintGuess:
        choices: list[str] | None = (
            trajectory.game_info
            if len(trajectory.turns) == 0
            else trajectory.turns[-1].feedback.next_choices
        )

        assert choices is not None
        return ContextoHintGuess(index=len(choices) - 1)

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        final_result: list[str] | None,
    ) -> Iterator[tuple[str, str]]:
        yield self._format_choices(turn_id=1, choices=trajectory.game_info, top_words=final_result)

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        turn_id: int,
        guess: ContextoHintGuess,
        final_result: list[str] | None,
    ) -> Iterator[tuple[str, str]]:
        choices: list[str] | None = (
            trajectory.game_info
            if turn_id == 0
            else trajectory.turns[turn_id - 1].feedback.next_choices
        )

        assert choices is not None
        index: int = guess.index

        yield (
            self.prompt_config.guess.guess,
            f"{index} ({choices[index] if 0 <= index < len(choices) else 'N/A'})",
        )

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        turn_id: int,
        guess: ContextoHintGuess,
        feedback: ContextoHintFeedback,
        final_result: list[str] | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: ContextoHintFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if feedback.distance >= 0:
            yield prompt.result, prompt.accept
            yield prompt.position, str(feedback.distance + 1)
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

        if feedback.next_choices is not None:
            yield self._format_choices(
                turn_id=turn_id + 2, choices=feedback.next_choices, top_words=final_result
            )

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[list[str], ContextoHintGuess, ContextoHintFeedback],
        final_result: list[str],
    ) -> Iterator[tuple[str, str]]:
        prompt: ContextoHintFinalResultPrompterPromptConfig = self.prompt_config.final_result
        yield prompt.secret_word, final_result[0]
        yield prompt.top_words, join_or_na(final_result[:30])

    def _format_choices(
        self, *, turn_id: int, choices: list[str], top_words: list[str] | None
    ) -> tuple[str, str]:
        word_pos: dict[str, int] | None = (
            None if top_words is None else {word: pos + 1 for pos, word in enumerate(top_words)}
        )

        return self.prompt_config.choices.format(turn_id=turn_id), join_or_na(
            f"{index}. {word}" + ("" if word_pos is None else f" ({word_pos[word]})")
            for index, word in enumerate(choices)
        )
