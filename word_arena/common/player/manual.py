from abc import ABC, abstractmethod
from typing import override

from .log import BaseLogPlayer


class BaseManualPlayer[IT, HT, GT, FT](BaseLogPlayer[IT, HT, GT, FT], ABC):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: IT) -> None:
        super().prepare(game_info=game_info)
        self._num_guesses: int = 0

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        super().digest(hint=hint, guess=guess, feedback=feedback)
        self._num_guesses += 1

    @override
    def make_guess(self, *, hint: HT) -> GT:
        return self.parse_guess(
            hint=hint, guess_str=input(f"Input Guess {self._num_guesses + 1}: ")
        )

    @abstractmethod
    def parse_guess(self, *, hint: HT, guess_str: str) -> GT:
        raise NotImplementedError()
