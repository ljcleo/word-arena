from abc import ABC, abstractmethod
from collections.abc import Iterator


class BaseInGameFormatter[IT, HT, GT, FT](ABC):
    @staticmethod
    @abstractmethod
    def format_game_info(*, game_info: IT) -> Iterator[str]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def format_hint(*, game_info: IT, hint: HT) -> Iterator[str]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def format_guess(*, game_info: IT, hint: HT, guess: GT) -> Iterator[str]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def format_feedback(*, game_info: IT, hint: HT, guess: GT, feedback: FT) -> Iterator[str]:
        raise NotImplementedError()


class BaseFinalResultFormatter[RT](ABC):
    @staticmethod
    @abstractmethod
    def format_final_result(*, final_result: RT) -> Iterator[str]:
        raise NotImplementedError()
