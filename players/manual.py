from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from common.player import BasePlayer


class BaseManualPlayer[GT, PT, AT, RT](BasePlayer[GT, PT, AT, RT], ABC):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: GT) -> None:
        self._num_guesses: int = 0

    @override
    def guess(self, *, hint: PT) -> AT:
        for section in self.format_hint(hint=hint):
            print(section)

        return self.process_guess(hint=hint, raw_guess=input("Guess: "))

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        for section in self.format_result(hint=hint, guess=guess, result=result):
            print(section)

        self._num_guesses += 1

    @abstractmethod
    def format_hint(self, *, hint: PT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, hint: PT, raw_guess: str) -> AT:
        raise NotImplementedError()

    @abstractmethod
    def format_result(self, *, hint: PT, guess: AT, result: RT) -> Iterator[str]:
        raise NotImplementedError()
