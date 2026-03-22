from collections.abc import Callable, Generator
from typing import override

from pydantic import BaseModel

from ..common.llm.engine.base import BaseLLMEngine


class ManualInputLLMConfig(BaseModel): ...


class ManualInputLLMEngine(BaseLLMEngine[ManualInputLLMConfig, None]):
    @property
    def input_func(self) -> Callable[[str], str]:
        return self._input_func

    @input_func.setter
    def input_func(self, input_func: Callable[[str], str]) -> None:
        self._input_func: Callable[[str], str] = input_func

    @override
    def make_human_message(self, *, content: str) -> None: ...

    @override
    def make_ai_message(self, *, content: str) -> None: ...

    @override
    def query(
        self, *messages: None, format: type[BaseModel] | None, system_instruction: str | None
    ) -> Generator[str, None, str]:
        yield from ()
        return self.input_func("Input AI response: ").strip()
