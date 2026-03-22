from collections.abc import Generator
from logging import WARNING, getLogger
from typing import Literal, override

from anthropic import Anthropic, omit
from anthropic.types import MessageParam
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.common import Message, MessageType
from ..common.llm.engine.base import BaseLLMEngine


class AnthropicLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    thinking_effort: Literal["low", "medium", "high", "max"] = "high"
    max_tokens: int = 32768
    timeout: int = 7200


class AnthropicLLMEngine(BaseLLMEngine[AnthropicLLMConfig]):
    def __init__(self, *, config: AnthropicLLMConfig) -> None:
        super().__init__(config=config)

        self._client: Anthropic = Anthropic(
            api_key=self.config.api_key, base_url=self.config.base_url, timeout=self.config.timeout
        )

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> Generator[str, None, str | T]:
        chat_messages: list[MessageParam] = []

        for message in messages:
            if message.role == MessageType.HUMAN:
                chat_messages.append({"role": "user", "content": message.content})
            elif message.role == MessageType.AI:
                chat_messages.append({"role": "assistant", "content": message.content})
            else:
                raise RuntimeError(message.role)

        answer_parts: list[str] = []
        parsed: T | None = None

        with self._client.messages.stream(
            messages=chat_messages,
            model=self.config.model,
            system=omit if system_instruction is None else system_instruction,
            output_format=omit if format is None else format,
            thinking={"type": "adaptive"},
            output_config={"effort": self.config.thinking_effort},
            max_tokens=self.config.max_tokens,
        ) as stream:
            buffer: list[str] = []

            for event in stream:
                if event.type == "content_block_start":
                    buffer.clear()
                elif event.type == "content_block_delta":
                    if event.delta.type == "thinking_delta":
                        buffer.append(event.delta.thinking)
                elif event.type == "content_block_stop":
                    if len(buffer) > 0:
                        yield "".join(buffer)
                        buffer.clear()

            for content in stream.get_final_message().content:
                if content.type == "text":
                    if format is None:
                        answer_parts.append(content.text)
                    elif content.parsed_output is not None:
                        parsed = content.parsed_output

        if format is None:
            return "".join(answer_parts)
        else:
            assert parsed is not None
            return parsed
