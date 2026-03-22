from abc import ABC, abstractmethod
from collections.abc import Generator

from pydantic import BaseModel

from ..common import Message


class BaseLLMEngine[CT](ABC):
    def __init__(self, *, config: CT) -> None:
        self._config: CT = config

    @property
    def config(self) -> CT:
        return self._config

    @abstractmethod
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> Generator[str, None, str | T]: ...
