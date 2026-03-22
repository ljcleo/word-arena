from collections.abc import Generator
from typing import override

from openai import OpenAI, omit
from openai.types.responses import EasyInputMessageParam, ParsedResponse
from openai.types.shared.reasoning_effort import ReasoningEffort
from pydantic import BaseModel

from ..common.llm.engine.base import BaseLLMEngine


class OpenaiResponsesLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    reasoning_effort: ReasoningEffort = "high"
    max_output_tokens: int = 32768
    use_system_message: bool = False
    timeout: int = 7200


class OpenaiResponsesLLMEngine(BaseLLMEngine[OpenaiResponsesLLMConfig, EasyInputMessageParam]):
    def __init__(self, *, config: OpenaiResponsesLLMConfig) -> None:
        super().__init__(config=config)

        self._client: OpenAI = OpenAI(
            api_key=self.config.api_key, base_url=self.config.base_url, timeout=self.config.timeout
        )

    @override
    def make_human_message(self, *, content: str) -> EasyInputMessageParam:
        return {"role": "user", "content": content}

    @override
    def make_ai_message(self, *, content: str) -> EasyInputMessageParam:
        return {"role": "assistant", "content": content}

    @override
    def query(
        self,
        *messages: EasyInputMessageParam,
        format: type[BaseModel] | None,
        system_instruction: str | None,
    ) -> Generator[str, None, str]:
        if self.config.use_system_message and system_instruction is not None:
            messages = ({"role": "developer", "content": system_instruction}, *messages)
            system_instruction = None

        with self._client.responses.stream(
            input=list(messages),
            model=self.config.model,
            instructions=omit if system_instruction is None else system_instruction,
            text_format=omit if format is None else format,
            reasoning={"effort": self.config.reasoning_effort},
            max_output_tokens=self.config.max_output_tokens,
            store=False,
        ) as stream:
            response: ParsedResponse[BaseModel] = stream.get_final_response()

        yield from ()
        return response.output_text
