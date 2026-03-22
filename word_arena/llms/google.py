from collections.abc import Generator
from logging import WARNING, getLogger
from typing import Literal, override

from google.genai import Client
from google.genai.types import (
    Content,
    GenerateContentConfig,
    HttpOptions,
    Part,
    ThinkingConfig,
    ThinkingLevel,
)
from pydantic import BaseModel
from tenacity import before_sleep_log, retry, wait_random

from ..common.llm.common import Message, MessageType
from ..common.llm.engine.base import BaseLLMEngine


class GoogleLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    thinking_level: ThinkingLevel = ThinkingLevel.HIGH
    max_output_tokens: int = 32768
    timeout: int = 7200


class GoogleLLMEngine(BaseLLMEngine[GoogleLLMConfig]):
    def __init__(self, *, config: GoogleLLMConfig) -> None:
        super().__init__(config=config)

        self._client: Client = Client(
            api_key=self.config.api_key,
            http_options=HttpOptions(base_url=self.config.base_url, timeout=self.config.timeout),
        )

    @retry(wait=wait_random(max=3), before_sleep=before_sleep_log(getLogger(__name__), WARNING))
    @override
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> Generator[str, None, str | T]:
        chat_messages: list[Content] = []

        for message in messages:
            if message.role == MessageType.HUMAN:
                chat_messages.append(Content(role="user", parts=[Part(message.content)]))
            elif message.role == MessageType.AI:
                chat_messages.append(Content(role="model", parts=[Part(message.content)]))
            else:
                raise RuntimeError(message.role)

        response_mime_type: Literal["application/json"] | None = None
        response_json_schema: dict | None = None

        if format is not None:
            response_mime_type = "application/json"
            response_json_schema = format.model_json_schema()

        answer_parts: list[str] = []

        for chunk in self._client.models.generate_content_stream(
            contents=chat_messages,
            model=self.config.model,
            config=GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
                response_json_schema=response_json_schema,
                thinking_config=ThinkingConfig(
                    include_thoughts=True, thinking_level=self.config.thinking_level
                ),
                max_output_tokens=self.config.max_output_tokens,
            ),
        ):
            if chunk.candidates is not None:
                content: Content | None = chunk.candidates[0].content
                if content is not None:
                    parts: list[Part] | None = content.parts
                    if parts is not None:
                        for part in parts:
                            text: str | None = part.text
                            if text is not None:
                                if part.thought:
                                    yield text
                                else:
                                    answer_parts.append(text)

        assert len(answer_parts) > 0
        answer: str = "".join(answer_parts)
        return answer if format is None else format.model_validate_json(answer)
