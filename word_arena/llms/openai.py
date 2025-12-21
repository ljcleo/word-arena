import logging
from dataclasses import dataclass
from typing import override
from uuid import uuid4

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


@dataclass(kw_only=True)
class OpenaiLLM(BaseLLM):
    api_key: str
    base_url: str
    model: str
    max_tokens: int
    timeout: int
    use_dev_message: bool
    log_file: str | None = None

    def __post_init__(self) -> None:
        self._client: OpenAI = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self._debug_logger: logging.Logger | None = None

        if self.log_file is not None:
            handler: logging.FileHandler = logging.FileHandler(self.log_file)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self._debug_logger = logging.getLogger(uuid4().hex)
            self._debug_logger.setLevel(logging.DEBUG)
            self._debug_logger.addHandler(handler)

    @retry(
        wait=wait_random(max=1),
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    )
    @override
    def query(self, *messages: Message) -> str:
        if self._debug_logger is not None:
            self._debug_logger.debug("new query:")
            for message in messages:
                self._debug_logger.debug(message.model_dump_json())

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

    @retry(
        wait=wait_random(max=1),
        before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    )
    @override
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        if self._debug_logger is not None:
            self._debug_logger.debug(f"new parse for {format}:")
            for message in messages:
                self._debug_logger.debug(message.model_dump_json())

        parsed: T | None = (
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

        assert parsed is not None
        return parsed

    def _convert(self, message: Message) -> ChatCompletionMessageParam:
        if message.role == MessageType.SYSTEM:
            if self.use_dev_message:
                return {"role": "developer", "content": message.content}
            else:
                return {"role": "system", "content": message.content}
        elif message.role == MessageType.HUMAN:
            return {"role": "user", "content": message.content}
        elif message.role == MessageType.AI:
            return {"role": "assistant", "content": message.content}
        else:
            raise RuntimeError(message.role)
