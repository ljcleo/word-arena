from abc import ABC, abstractmethod

from pydantic import BaseModel

from .common import Message


class BaseLLM(ABC):
    @abstractmethod
    def query(self, *messages: Message) -> str:
        raise NotImplementedError()

    @abstractmethod
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        raise NotImplementedError()
