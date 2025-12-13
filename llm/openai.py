from dataclasses import dataclass
from logging import WARNING, getLogger
from typing import override

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from llm.common import BaseLLM, Message, MessageType


@dataclass(kw_only=True)
class OpenAILLM(BaseLLM):
    api_key: str
    base_url: str
    model: str
    max_tokens: int
    timeout: int

    def __post_init__(self) -> None:
        self._client: OpenAI = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @retry(wait=wait_random(max=1), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def query(self, *messages: Message) -> str:
        return str(
            self._client.chat.completions.create(
                messages=list(map(self._convert, messages)),
                model=self.model,
                max_completion_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            .choices[0]
            .message.content
        )

    @retry(wait=wait_random(max=1), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        result: T | None = (
            self._client.chat.completions.parse(
                messages=list(map(self._convert, messages)),
                model=self.model,
                response_format=format,
                max_completion_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            .choices[0]
            .message.parsed
        )

        assert result is not None
        return result

    @staticmethod
    def _convert(message: Message) -> ChatCompletionMessageParam:
        if message.role == MessageType.SYSTEM:
            return {"role": "system", "content": message.content}
        elif message.role == MessageType.HUMAN:
            return {"role": "user", "content": message.content}
        elif message.role == MessageType.AI:
            return {"role": "assistant", "content": message.content}
        else:
            raise RuntimeError(message.role)
