from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from common.player import BasePlayer


class BaseIOPlayer[IT, HT, GT, FT](BasePlayer[IT, HT, GT, FT], ABC):
    @override
    def guess(self, *, hint: HT) -> GT:
        for section in self.format_hint(hint=hint):
            print(section)

        guess: GT = self.process_guess(hint=hint, raw_guess=self.make_raw_guess(hint=hint))
        print("Processed Guess:", guess)
        return guess

    @override
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        for section in self.format_feedback(hint=hint, guess=guess, feedback=feedback):
            print(section)

    @abstractmethod
    def format_hint(self, *, hint: HT) -> Iterator[str]:
        raise NotImplementedError()

    @abstractmethod
    def make_raw_guess(self, *, hint: HT) -> str:
        raise NotImplementedError()

    @abstractmethod
    def process_guess(self, *, hint: HT, raw_guess: str) -> GT:
        raise NotImplementedError()

    @abstractmethod
    def format_feedback(self, *, hint: HT, guess: GT, feedback: FT) -> Iterator[str]:
        raise NotImplementedError()
