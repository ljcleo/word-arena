from abc import ABC, abstractmethod
from collections.abc import Iterator


class BaseInGameFormatter[IT, HT, GT, FT](ABC):
    @classmethod
    @abstractmethod
    def format_game_info(cls, *, game_info: IT) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def format_hint(cls, *, game_info: IT, hint: HT) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def format_guess(cls, *, game_info: IT, hint: HT, guess: GT) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def format_feedback(
        cls, *, game_info: IT, hint: HT, guess: GT, feedback: FT
    ) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()


class BaseFinalResultFormatter[RT](ABC):
    @classmethod
    @abstractmethod
    def format_final_result(cls, *, final_result: RT) -> Iterator[tuple[str, str]]:
        raise NotImplementedError()
