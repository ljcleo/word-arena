from collections.abc import Generator
from typing import Literal, override

from anthropic import Anthropic, omit
from anthropic.types import MessageParam
from pydantic import BaseModel

from ..common.llm.engine.base import BaseLLMEngine


class AnthropicLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    thinking_effort: Literal["low", "medium", "high", "max"] = "high"
    max_tokens: int = 32768
    timeout: int = 7200


class AnthropicLLMEngine(BaseLLMEngine[AnthropicLLMConfig, MessageParam]):
    def __init__(self, *, config: AnthropicLLMConfig) -> None:
        super().__init__(config=config)

        self._client: Anthropic = Anthropic(
            api_key=self.config.api_key, base_url=self.config.base_url, timeout=self.config.timeout
        )

    @override
    def make_human_message(self, *, content: str) -> MessageParam:
        return {"role": "user", "content": content}

    @override
    def make_ai_message(self, *, content: str) -> MessageParam:
        return {"role": "assistant", "content": content}

    @override
    def query(
        self,
        *messages: MessageParam,
        format: type[BaseModel] | None,
        system_instruction: str | None,
    ) -> Generator[str, None, str]:
        answer_parts: list[str] = []

        with self._client.messages.stream(
            messages=messages,
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
                    answer_parts.append(content.text)

        return "".join(answer_parts)
