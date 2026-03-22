from collections.abc import Generator
from typing import override

from pydantic import BaseModel

from ..common.llm.engine.base import BaseLLMEngine


class AutoReplyLLMConfig(BaseModel): ...


class AutoReplyLLMEngine(BaseLLMEngine[AutoReplyLLMConfig, str]):
    @override
    def make_human_message(self, *, content: str) -> str:
        return content

    @override
    def make_ai_message(self, *, content: str) -> str:
        return content

    @override
    def query(
        self, *messages: str, format: type[BaseModel] | None, system_instruction: str | None
    ) -> Generator[str, None, str]:
        yield from ()

        if format is None:
            return "This is an auto reply."
        else:
            return messages[-1].rsplit("\n", maxsplit=1)[-1].partition("`")[2].partition("`")[0]
