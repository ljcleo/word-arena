from abc import ABC, abstractmethod
from typing import override

from ..formatter.base import BaseInGameFormatter
from .base import BasePlayer


class BaseLogPlayer[IT, HT, GT, FT](BasePlayer[IT, HT, GT, FT], ABC):
    def __init__(self, *, in_game_formatter_cls: type[BaseInGameFormatter[IT, HT, GT, FT]]) -> None:
        self._in_game_formatter_cls: type[BaseInGameFormatter[IT, HT, GT, FT]] = (
            in_game_formatter_cls
        )

    @property
    def in_game_formatter_cls(self) -> type[BaseInGameFormatter[IT, HT, GT, FT]]:
        return self._in_game_formatter_cls

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._game_info: IT = game_info
        for section in self.in_game_formatter_cls.format_game_info(game_info=game_info):
            print(section)

    @override
    def guess(self, *, hint: HT) -> GT:
        for section in self.in_game_formatter_cls.format_hint(game_info=self._game_info, hint=hint):
            print(section)

        guess: GT = self.make_guess(hint=hint)

        for section in self.in_game_formatter_cls.format_guess(
            game_info=self._game_info, hint=hint, guess=guess
        ):
            print(section)

        return guess

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        for section in self.in_game_formatter_cls.format_feedback(
            game_info=self._game_info, hint=hint, guess=guess, feedback=feedback
        ):
            print(section)

    @abstractmethod
    def make_guess(self, *, hint: HT) -> GT:
        raise NotImplementedError()
