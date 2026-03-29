from collections.abc import Generator
from logging import WARNING, getLogger
from typing import Any, overload

from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from .common import Message, MessageType
from .engine.base import BaseLLMEngine
from .renderer.base import BaseLLMRenderer


class Stream:
    def __init__(self, generator: Generator[str, None, str], /) -> None:
        self._generator: Generator[str, None, str] = generator

    def __iter__(self) -> Generator[str, None, str]:
        self.value = yield from self._generator
        return self.value


class LLM[PT]:
    def __init__(self, *, engine: BaseLLMEngine[Any, PT], renderer: BaseLLMRenderer) -> None:
        self._engine: BaseLLMEngine[Any, PT] = engine
        self._renderer: BaseLLMRenderer = renderer

    @overload
    def query(self, *messages: Message, system_instruction: str | None = None) -> str: ...

    @overload
    def query[T: BaseModel](
        self, *messages: Message, format: type[T], system_instruction: str | None = None
    ) -> T: ...

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
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

        stream: Stream = Stream(
            self._engine.query(
                *(
                    (
                        self._engine.make_human_message
                        if message.role == MessageType.HUMAN
                        else self._engine.make_ai_message
                    )(content=message.content)
                    for message in messages
                ),
                format=format,
                system_instruction=system_instruction,
            )
        )

        for content in stream:
            self._renderer.render_message(message_type="AI-INTERNAL", content=content)

        result: str = stream.value

        self._renderer.render_message(
            message_type=MessageType.AI,
            content=result if isinstance(result, str) else result.model_dump_json(),
        )

        return result if format is None else format.model_validate_json(result, strict=True)
