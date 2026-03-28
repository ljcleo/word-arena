from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from ..common import Trajectory
from ..state import GameStateInterface
from .base import BaseGameRenderer


class BaseLogGameRenderer[PT, IT, GT, FT, RT](BaseGameRenderer[IT, GT, FT, RT], ABC):
    def __init__(self, *, game_log_func: Callable[[str, str], None], prompt_config: PT) -> None:
        self._game_log_func: Callable[[str, str], None] = game_log_func
        self._prompt_config: PT = prompt_config

    @property
    def prompt_config(self) -> PT:
        return self._prompt_config

    @override
    def render_game_info(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self.format_game_info(game_info=state.game_info))

    @override
    def render_guess(self, *, state: GameStateInterface[IT, GT, FT, RT], guess: GT) -> None:
        self._log(*self.format_guess(trajectory=state.trajectory, guess=guess))

    @override
    def render_last_feedback(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self.format_last_feedback(trajectory=state.trajectory))

    @override
    def render_final_result(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(
            ("Total Guesses", str(len(state.turns))),
            *self.format_final_result(trajectory=state.trajectory, final_result=state.final_result),
        )

    @abstractmethod
    def format_game_info(self, *, game_info: IT) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_guess(
        self, *, trajectory: Trajectory[IT, GT, FT], guess: GT
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_last_feedback(
        self, *, trajectory: Trajectory[IT, GT, FT]
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_final_result(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT
    ) -> Iterator[tuple[str, str]]: ...

    def _log(self, *output: tuple[str, str]):
        for key, value in output:
            self._game_log_func(key, value)
