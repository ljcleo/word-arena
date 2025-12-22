from abc import ABC, abstractmethod
from typing import override

from ..formatter.base import BaseInGameFormatter
from .base import BasePlayer


class BaseLogPlayer[IT, HT, GT, FT](
    BasePlayer[IT, HT, GT, FT], BaseInGameFormatter[IT, HT, GT, FT], ABC
):
    @override
    def prepare(self, *, game_info: IT) -> None:
        self._game_info: IT = game_info
        for section in self.format_game_info(game_info=game_info):
            print(section)

    @override
    def guess(self, *, hint: HT) -> GT:
        for section in self.format_hint(game_info=self._game_info, hint=hint):
            print(section)

        guess: GT = self.make_guess(hint=hint)

        for section in self.format_guess(game_info=self._game_info, hint=hint, guess=guess):
            print(section)

        return guess

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        for section in self.format_feedback(
            game_info=self._game_info, hint=hint, guess=guess, feedback=feedback
        ):
            print(section)

    @abstractmethod
    def make_guess(self, *, hint: HT) -> GT:
        raise NotImplementedError()
