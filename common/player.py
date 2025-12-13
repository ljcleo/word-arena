from abc import ABC, abstractmethod


class BasePlayer[GT, PT, AT, RT](ABC):
    @abstractmethod
    def prepare(self, *, game_info: GT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def guess(self, *, hint: PT) -> AT:
        raise NotImplementedError()

    @abstractmethod
    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        raise NotImplementedError()
