from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter, BaseAgentPrompterPromptConfig
from .....utils import join_or_na
from ...common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoWordGroup


class ConexoInfoPrompterPromptConfig(BaseModel):
    words: str
    group_size: str
    max_turns: str
    unlimited: str


class ConexoGuessPrompterPromptConfig(BaseModel):
    guess_detail: str
    guess: str


class ConexoFeedbackPrompterPromptConfig(BaseModel):
    result: str
    accept: str
    theme: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ConexoFinalResultPrompterPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_groups: str
    remaining_groups: str


class ConexoAgentPrompterPromptConfig(BaseAgentPrompterPromptConfig):
    game_info: ConexoInfoPrompterPromptConfig
    guess: ConexoGuessPrompterPromptConfig
    feedback: ConexoFeedbackPrompterPromptConfig
    final_result: ConexoFinalResultPrompterPromptConfig


class ConexoAgentPrompter(
    BaseAgentPrompter[
        ConexoAgentPrompterPromptConfig, ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult
    ]
):
    GUESS_CLS = ConexoGuess

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback]
    ) -> str:
        example: range = range(trajectory.game_info.group_size)

        return self.prompt_config.guess.guess_detail.format(
            response=join_or_na(map(str, example)),
            choices=join_or_na(trajectory.game_info.words[index] for index in example),
        )

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback]
    ) -> ConexoGuess:
        return ConexoGuess(indices=list(range(trajectory.game_info.group_size)))

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: ConexoInfo = trajectory.game_info
        prompt: ConexoInfoPrompterPromptConfig = self.prompt_config.game_info

        yield (
            prompt.words,
            join_or_na(f"{index}. {word}" for index, word in enumerate(game_info.words)),
        )

        yield prompt.group_size, str(game_info.group_size)

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        turn_id: int,
        guess: ConexoGuess,
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        words: list[str] = trajectory.game_info.words

        yield (
            self.prompt_config.guess.guess,
            join_or_na(
                f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"
                for index in guess.indices
            ),
        )

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        turn_id: int,
        guess: ConexoGuess,
        feedback: ConexoFeedback,
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        prompt: ConexoFeedbackPrompterPromptConfig = self.prompt_config.feedback

        if feedback.accepted:
            yield prompt.result, prompt.accept
            yield prompt.theme, "N/A" if feedback.message is None else feedback.message
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        final_result: ConexoFinalResult,
    ) -> Iterator[tuple[str, str]]:
        victory: bool = len(final_result.remaining_groups) == 0
        prompt: ConexoFinalResultPrompterPromptConfig = self.prompt_config.final_result
        yield prompt.result, prompt.verdicts[victory]
        yield prompt.found_groups, self._format_groups(groups=final_result.found_groups)

        if not victory:
            yield (
                prompt.remaining_groups,
                self._format_groups(groups=final_result.remaining_groups),
            )

    def _format_groups(self, *, groups: Iterable[ConexoWordGroup]) -> str:
        return join_or_na(f"{'/'.join(group.words)} ({group.theme})" for group in groups)
