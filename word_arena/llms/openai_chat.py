from logging import WARNING, getLogger
from typing import Literal, overload, override

from openai import OpenAI, omit
from openai.types.chat import ChatCompletionMessageParam, ParsedChatCompletionMessage
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


class OpenaiChatLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 32768
    system_key: Literal["developer", "system"] = "developer"
    use_max_completion_tokens: bool = True
    timeout: int = 7200


class OpenaiChatLLM(BaseLLM):
    def __init__(self, *, config: OpenaiChatLLMConfig) -> None:
        self._config: OpenaiChatLLMConfig = config

        self._client: OpenAI = OpenAI(
            api_key=config.api_key, base_url=config.base_url, timeout=self._config.timeout
        )

    @overload
    def query(self, *messages: Message, system_instruction: str | None = None) -> str: ...

    @overload
    def query[T: BaseModel](
        self, *messages: Message, format: type[T], system_instruction: str | None = None
    ) -> T: ...

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> str | T:
        chat_messages: list[ChatCompletionMessageParam] = []

        if system_instruction is not None:
            chat_messages.append(
                {"role": self._config.system_key, "content": system_instruction}
                if self._config.system_key == "developer"
                else {"role": self._config.system_key, "content": system_instruction}
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
            model=self._config.model,
            response_format=omit if format is None else format,
            max_completion_tokens=self._config.max_tokens
            if self._config.use_max_completion_tokens
            else omit,
            max_tokens=omit if self._config.use_max_completion_tokens else self._config.max_tokens,
        ) as stream:
            response: ParsedChatCompletionMessage[T] = (
                stream.get_final_completion().choices[0].message
            )

        if format is None:
            return str(response.content)
        else:
            parsed: T | None = response.parsed
            assert parsed is not None
            return parsed
