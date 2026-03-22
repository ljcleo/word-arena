from abc import ABC, abstractmethod
from collections.abc import Generator

from pydantic import BaseModel


class BaseLLMEngine[CT, PT](ABC):
    def __init__(self, *, config: CT) -> None:
        self._config: CT = config

    @property
    def config(self) -> CT:
        return self._config

    @abstractmethod
    def make_human_message(self, *, content: str) -> PT: ...

    @abstractmethod
    def make_ai_message(self, *, content: str) -> PT: ...

    @abstractmethod
    def query(
        self, *messages: PT, format: type[BaseModel] | None, system_instruction: str | None
    ) -> Generator[str, None, str]: ...
