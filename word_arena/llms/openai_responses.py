from collections.abc import Generator
from logging import WARNING, getLogger
from typing import override

from openai import OpenAI, omit
from openai.types.responses import ParsedResponse, ResponseInputItemParam
from openai.types.shared.reasoning_effort import ReasoningEffort
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.common import Message, MessageType
from ..common.llm.engine.base import BaseLLMEngine


class OpenaiResponsesLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    reasoning_effort: ReasoningEffort = "high"
    max_output_tokens: int = 32768
    use_system_message: bool = False
    timeout: int = 7200


class OpenaiResponsesLLMEngine(BaseLLMEngine[OpenaiResponsesLLMConfig]):
    def __init__(self, *, config: OpenaiResponsesLLMConfig) -> None:
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
        chat_messages: list[ResponseInputItemParam] = []

        if self.config.use_system_message and system_instruction is not None:
            chat_messages.append({"role": "developer", "content": system_instruction})
            system_instruction = None

        for message in messages:
            if message.role == MessageType.HUMAN:
                chat_messages.append({"role": "user", "content": message.content})
            elif message.role == MessageType.AI:
                chat_messages.append({"role": "assistant", "content": message.content})
            else:
                raise RuntimeError(message.role)

        with self._client.responses.stream(
            input=chat_messages,
            model=self.config.model,
            instructions=omit if system_instruction is None else system_instruction,
            text_format=omit if format is None else format,
            reasoning={"effort": self.config.reasoning_effort},
            max_output_tokens=self.config.max_output_tokens,
            store=False,
        ) as stream:
            response: ParsedResponse[T] = stream.get_final_response()

        yield from ()

        if format is None:
            return response.output_text
        else:
            parsed: T | None = response.output_parsed
            assert parsed is not None
            return parsed
