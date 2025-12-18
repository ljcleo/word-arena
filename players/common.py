from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from common.player import BasePlayer


class BaseIOPlayer[GT, PT, AT, RT](BasePlayer[GT, PT, AT, RT], ABC):
    @override
    def guess(self, *, hint: PT) -> AT:
        for section in self.format_hint(hint=hint):
            print(section)

        guess: AT = self.process_guess(hint=hint, raw_guess=self.make_raw_guess(hint=hint))
        print("Processed Guess:", guess)
        return guess

    @override
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        for section in self.format_result(hint=hint, guess=guess, result=result):
            print(section)

    @abstractmethod
    def format_hint(self, *, hint: PT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_raw_guess(self, *, hint: PT) -> str:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, hint: PT, raw_guess: str) -> AT:
        raise NotImplementedError()

    @abstractmethod
    def format_result(self, *, hint: PT, guess: AT, result: RT) -> Iterator[str]:
        raise NotImplementedError()
