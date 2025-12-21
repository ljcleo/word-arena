from abc import ABC, abstractmethod


class BasePlayer[IT, HT, GT, FT](ABC):
    @abstractmethod
    def prepare(self, *, game_info: IT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def guess(self, *, hint: HT) -> GT:
        raise NotImplementedError()

    @abstractmethod
    def digest(self, *, hint: HT, guess: GT, feedback: FT) -> None:
        raise NotImplementedError()
