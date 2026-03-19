from abc import ABC, abstractmethod
from typing import overload

from pydantic import BaseModel

from .common import Message


class BaseLLM(ABC):
    @overload
    def query(self, *messages: Message, system_instruction: str | None = None) -> str: ...

    @overload
    def query[T: BaseModel](
        self, *messages: Message, format: type[T], system_instruction: str | None = None
    ) -> T: ...

    @abstractmethod
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> str | T: ...
