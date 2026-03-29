from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsWordGroup,
)


class ConnectionsInfoLogPromptConfig(BaseModel):
    words: str
    group_size: str
    max_turns: str
    unlimited: str


class ConnectionsFeedbackLogPromptConfig(BaseModel):
    result: str
    accept: str
    theme: str
    reject: str
    reject_reason: str
    invalid_guess: str


class ConnectionsFinalResultLogPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_groups: str
    remaining_groups: str


class ConnectionsLogPromptConfig(BaseModel):
    game_info: ConnectionsInfoLogPromptConfig
    guess: str
    feedback: ConnectionsFeedbackLogPromptConfig
    final_result: ConnectionsFinalResultLogPromptConfig


class ConnectionsLogGameRenderer(
    BaseLogGameRenderer[
        ConnectionsLogPromptConfig,
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
    ]
):
    @override
    def format_game_info(self, *, game_info: ConnectionsInfo) -> Iterator[tuple[str, str]]:
        prompt: ConnectionsInfoLogPromptConfig = self.prompt_config.game_info

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
    def format_guess(
        self,
        *,
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        guess: ConnectionsGuess,
    ) -> Iterator[tuple[str, str]]:
        words: list[str] = trajectory.game_info.words

        yield (
            self.prompt_config.guess,
            join_or_na(
                f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"
                for index in guess.indices
            ),
        )

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: ConnectionsFeedback = trajectory.turns[-1].feedback
        prompt: ConnectionsFeedbackLogPromptConfig = self.prompt_config.feedback

        if feedback.accepted:
            yield prompt.result, prompt.accept
            yield prompt.theme, "N/A" if feedback.message is None else feedback.message
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.invalid_guess

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        final_result: ConnectionsFinalResult,
    ) -> Iterator[tuple[str, str]]:
        victory: bool = len(final_result.remaining_groups) == 0
        prompt: ConnectionsFinalResultLogPromptConfig = self.prompt_config.final_result
        yield prompt.result, prompt.verdicts[victory]
        yield prompt.found_groups, self._format_groups(groups=final_result.found_groups)

        if not victory:
            yield (
                prompt.remaining_groups,
                self._format_groups(groups=final_result.remaining_groups),
            )

    @classmethod
    def _format_groups(cls, *, groups: Iterable[ConnectionsWordGroup]) -> str:
        return join_or_na(f"{'/'.join(group.words)} ({group.theme})" for group in groups)
