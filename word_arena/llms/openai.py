from logging import WARNING, getLogger
from typing import override

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


class OpenaiConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    max_tokens: int
    timeout: int
    use_dev_message: bool


class OpenaiLLM(BaseLLM):
    def __init__(self, *, config: OpenaiConfig) -> None:
        self._model: str = config.model
        self._max_tokens: int = config.max_tokens
        self._timeout: int = config.timeout
        self._use_dev_message: bool = config.use_dev_message
        self._client: OpenAI = OpenAI(api_key=config.api_key, base_url=config.base_url)

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def query(self, *messages: Message) -> str:
        return str(
            self._client.chat.completions.create(
                messages=list(map(self._convert, messages)),
                model=self._model,
                max_completion_tokens=self._max_tokens,
                timeout=self._timeout,
            )
            .choices[0]
            .message.content
        )

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        parsed: T | None = (
            self._client.chat.completions.parse(
                messages=list(map(self._convert, messages)),
                model=self._model,
                response_format=format,
                max_completion_tokens=self._max_tokens,
                timeout=self._timeout,
            )
            .choices[0]
            .message.parsed
        )

        assert parsed is not None
        return parsed

    def _convert(self, message: Message) -> ChatCompletionMessageParam:
        if message.role == MessageType.SYSTEM:
            if self._use_dev_message:
                return {"role": "developer", "content": message.content}
            else:
                return {"role": "system", "content": message.content}
        elif message.role == MessageType.HUMAN:
            return {"role": "user", "content": message.content}
        elif message.role == MessageType.AI:
            return {"role": "assistant", "content": message.content}
        else:
            raise RuntimeError(message.role)
