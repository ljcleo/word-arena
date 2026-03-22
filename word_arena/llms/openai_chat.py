from collections.abc import Generator
from typing import Literal, override

from openai import OpenAI, omit
from openai.types.chat import ChatCompletionMessageParam, ParsedChatCompletionMessage
from pydantic import BaseModel

from ..common.llm.engine.base import BaseLLMEngine


class OpenaiChatLLMConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 32768
    system_key: Literal["developer", "system"] = "developer"
    use_max_completion_tokens: bool = True
    timeout: int = 7200


class OpenaiChatLLMEngine(BaseLLMEngine[OpenaiChatLLMConfig, ChatCompletionMessageParam]):
    def __init__(self, *, config: OpenaiChatLLMConfig) -> None:
        super().__init__(config=config)

        self._client: OpenAI = OpenAI(
            api_key=self.config.api_key, base_url=self.config.base_url, timeout=self.config.timeout
        )

    @override
    def make_human_message(self, *, content: str) -> ChatCompletionMessageParam:
        return {"role": "user", "content": content}

    @override
    def make_ai_message(self, *, content: str) -> ChatCompletionMessageParam:
        return {"role": "assistant", "content": content}

    @override
    def query(
        self,
        *messages: ChatCompletionMessageParam,
        format: type[BaseModel] | None,
        system_instruction: str | None,
    ) -> Generator[str, None, str]:
        if system_instruction is not None:
            messages = (
                {"role": self.config.system_key, "content": system_instruction}
                if self.config.system_key == "developer"
                else {"role": self.config.system_key, "content": system_instruction},
                *messages,
            )

        with self._client.chat.completions.stream(
            messages=messages,
            model=self.config.model,
            response_format=omit if format is None else format,
            max_completion_tokens=self.config.max_tokens
            if self.config.use_max_completion_tokens
            else omit,
            max_tokens=omit if self.config.use_max_completion_tokens else self.config.max_tokens,
        ) as stream:
            response: ParsedChatCompletionMessage[BaseModel] = (
                stream.get_final_completion().choices[0].message
            )

        yield from ()
        return str(response.content)
