from abc import ABC
from typing import override

from players.common import BaseIOPlayer


class BaseManualPlayer[GT, PT, AT, RT](BaseIOPlayer[GT, PT, AT, RT], ABC):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._num_guesses: int = 0

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        super().digest(hint=hint, guess=guess, result=result)
        self._num_guesses += 1

    @override
    def make_raw_guess(self, *, hint: PT) -> str:
        return input("Guess: ")
