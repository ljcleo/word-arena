from collections.abc import Generator
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

from ..common.llm.engine.base import BaseLLMEngine


class GoogleLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    thinking_level: ThinkingLevel = ThinkingLevel.HIGH
    max_output_tokens: int = 32768
    timeout: int = 7200


class GoogleLLMEngine(BaseLLMEngine[GoogleLLMConfig, Content]):
    def __init__(self, *, config: GoogleLLMConfig) -> None:
        super().__init__(config=config)

        self._client: Client = Client(
            api_key=self.config.api_key,
            http_options=HttpOptions(base_url=self.config.base_url, timeout=self.config.timeout),
        )

    @override
    def make_human_message(self, *, content: str) -> Content:
        return Content(parts=[Part(content)], role="user")

    @override
    def make_ai_message(self, *, content: str) -> Content:
        return Content(parts=[Part(content)], role="model")

    @override
    def query(
        self, *messages: Content, format: type[BaseModel] | None, system_instruction: str | None
    ) -> Generator[str, None, str]:
        response_mime_type: Literal["application/json"] | None = None
        response_json_schema: dict | None = None

        if format is not None:
            response_mime_type = "application/json"
            response_json_schema = format.model_json_schema()

        answer_parts: list[str] = []

        for chunk in self._client.models.generate_content_stream(
            contents=messages,
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

        return "".join(answer_parts)
