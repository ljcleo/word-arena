from collections.abc import Generator
from typing import Any, overload

from pydantic import BaseModel

from .common import Message, MessageType
from .engine.base import BaseLLMEngine
from .renderer.base import BaseLLMRenderer


class LLM:
    def __init__(self, *, engine: BaseLLMEngine[Any], renderer: BaseLLMRenderer) -> None:
        self._engine: BaseLLMEngine[Any] = engine
        self._renderer: BaseLLMRenderer = renderer

    @overload
    def query(self, *messages: Message, system_instruction: str | None = None) -> str: ...

    @overload
    def query[T: BaseModel](
        self, *messages: Message, format: type[T], system_instruction: str | None = None
    ) -> T: ...

    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> str | T:
        if system_instruction is not None:
            self._renderer.render_message(message_type="SYSTEM", content=system_instruction)
        for message in messages:
            self._renderer.render_message(message_type=message.role, content=message.content)

        class Stream:
            def __init__(self, generator: Generator[str, None, str | T], /) -> None:
                self._generator: Generator[str, None, str | T] = generator

            def __iter__(self) -> Generator[str, None, str | T]:
                self.value = yield from self._generator
                return self.value

        stream: Stream = Stream(
            self._engine.query(*messages, format=format, system_instruction=system_instruction)
        )

        for content in stream:
            self._renderer.render_message(message_type="AI-INTERNAL", content=content)

        result: str | T = stream.value

        self._renderer.render_message(
            message_type=MessageType.AI,
            content=result if isinstance(result, str) else result.model_dump_json(),
        )

        return result
