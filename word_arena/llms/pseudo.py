from collections.abc import Generator
from typing import override

from pydantic import BaseModel

from ..common.llm.common import Message
from ..common.llm.engine.base import BaseLLMEngine


class PseudoLLMConfig(BaseModel):
    auto_reply: bool


class PseudoLLMEngine(BaseLLMEngine[PseudoLLMConfig]):
    @override
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> Generator[str, None, str | T]:
        if self.config.auto_reply:
            reply: str = (
                messages[-1]
                .content.rsplit("\n", maxsplit=1)[-1]
                .partition("`")[2]
                .partition("`")[0]
                if format is not None
                else "This is an auto reply."
            )
        else:
            reply = input("Input AI response: ").strip()

        yield from ()
        return reply if format is None else format.model_validate_json(reply)
