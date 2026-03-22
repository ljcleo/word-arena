from collections.abc import Generator
from logging import WARNING, getLogger
from typing import Literal, override

from openai import OpenAI, omit
from openai.types.chat import ChatCompletionMessageParam, ParsedChatCompletionMessage
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.common import Message, MessageType
from ..common.llm.engine.base import BaseLLMEngine


class OpenaiChatLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 32768
    system_key: Literal["developer", "system"] = "developer"
    use_max_completion_tokens: bool = True
    timeout: int = 7200


class OpenaiChatLLMEngine(BaseLLMEngine[OpenaiChatLLMConfig]):
    def __init__(self, *, config: OpenaiChatLLMConfig) -> None:
        super().__init__(config=config)

        self._client: OpenAI = OpenAI(
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
        chat_messages: list[ChatCompletionMessageParam] = []

        if system_instruction is not None:
            chat_messages.append(
                {"role": self.config.system_key, "content": system_instruction}
                if self.config.system_key == "developer"
                else {"role": self.config.system_key, "content": system_instruction}
            )

        for message in messages:
            if message.role == MessageType.HUMAN:
                chat_messages.append({"role": "user", "content": message.content})
            elif message.role == MessageType.AI:
                chat_messages.append({"role": "assistant", "content": message.content})
            else:
                raise RuntimeError(message.role)

        with self._client.chat.completions.stream(
            messages=chat_messages,
            model=self.config.model,
            response_format=omit if format is None else format,
            max_completion_tokens=self.config.max_tokens
            if self.config.use_max_completion_tokens
            else omit,
            max_tokens=omit if self.config.use_max_completion_tokens else self.config.max_tokens,
        ) as stream:
            response: ParsedChatCompletionMessage[T] = (
                stream.get_final_completion().choices[0].message
            )

        yield from ()

        if format is None:
            return str(response.content)
        else:
            parsed: T | None = response.parsed
            assert parsed is not None
            return parsed
