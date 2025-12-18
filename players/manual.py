from abc import ABC
from typing import override

from players.common import BaseIOPlayer


class BaseManualPlayer[IT, HT, GT, FT](BaseIOPlayer[IT, HT, GT, FT], ABC):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: IT) -> None:
        self._num_guesses: int = 0

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        super().digest(hint=hint, guess=guess, feedback=feedback)
        self._num_guesses += 1

    @override
    def make_raw_guess(self, *, hint: HT) -> str:
        return input("Guess: ")
