from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from ..formatter.base import BaseInGameFormatter
from .base import BasePlayer


class BaseLogPlayer[IT, HT, GT, FT](
    BasePlayer[IT, HT, GT, FT], BaseInGameFormatter[IT, HT, GT, FT], ABC
):
    def __init__(self, *, player_log_func: Callable[[str], None], **kwargs) -> None:
        super().__init__(**kwargs)
        self._player_log_func: Callable[[str], None] = player_log_func

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._game_info: IT = game_info
        for key, value in self.format_game_info(game_info=game_info):
            self._player_log_func(f"{key}: {value}")

    @override
    def guess(self, *, hint: HT) -> GT:
        for key, value in self.format_hint(game_info=self._game_info, hint=hint):
            self._player_log_func(f"{key}: {value}")

        guess: GT = self.make_guess(hint=hint)

        for key, value in self.format_guess(game_info=self._game_info, hint=hint, guess=guess):
            self._player_log_func(f"{key}: {value}")

        return guess

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        for key, value in self.format_feedback(
            game_info=self._game_info, hint=hint, guess=guess, feedback=feedback
        ):
            self._player_log_func(f"{key}: {value}")

    @abstractmethod
    def make_guess(self, *, hint: HT) -> GT:
        raise NotImplementedError()
