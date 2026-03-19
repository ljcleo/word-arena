from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from ..state import GameStateInterface
from .base import BaseGameRenderer


class BaseLogGameRenderer[IT, GT, FT, RT](BaseGameRenderer[IT, GT, FT, RT], ABC):
    def __init__(self, *, game_log_func: Callable[[str, str], None]) -> None:
        self._game_log_func: Callable[[str, str], None] = game_log_func

    @override
    def render_game_info(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self.format_game_info(state=state))

    @override
    def render_guess(self, *, state: GameStateInterface[IT, GT, FT, RT], guess: GT) -> None:
        self._log(*self.format_guess(state=state, guess=guess))

    @override
    def render_last_feedback(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self.format_last_feedback(state=state))

    @override
    def render_final_result(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(("Total Guesses", str(len(state.turns))), *self.format_final_result(state=state))

    @abstractmethod
    def format_game_info(
        self, *, state: GameStateInterface[IT, GT, FT, RT]
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_guess(
        self, *, state: GameStateInterface[IT, GT, FT, RT], guess: GT
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_last_feedback(
        self, *, state: GameStateInterface[IT, GT, FT, RT]
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def format_final_result(
        self, *, state: GameStateInterface[IT, GT, FT, RT]
    ) -> Iterator[tuple[str, str]]: ...

    def _log(self, *output: tuple[str, str]):
        for key, value in output:
            self._game_log_func(key, value)
