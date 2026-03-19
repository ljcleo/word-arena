from collections.abc import Callable
from typing import overload, override

from pydantic import BaseModel

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


class PseudoLLMConfig(BaseModel):
    auto_reply: bool


class PseudoLLM(BaseLLM):
    def __init__(
        self, *, config: PseudoLLMConfig, llm_log_func: Callable[[str, str], None]
    ) -> None:
        self._config: PseudoLLMConfig = config
        self._llm_log_func: Callable[[str, str], None] = llm_log_func

    @overload
    def query(self, *messages: Message, system_instruction: str | None = None) -> str: ...

    @overload
    def query[T: BaseModel](
        self, *messages: Message, format: type[T], system_instruction: str | None = None
    ) -> T: ...

    @override
    def query[T: BaseModel](
        self,
        *messages: Message,
        format: type[T] | None = None,
        system_instruction: str | None = None,
    ) -> str | T:
        if system_instruction is not None:
            self._llm_log_func("SYSTEM INSTRUCTION", system_instruction)
        for message in messages:
            self._llm_log_func(str(message.role), message.content)

        if self._config.auto_reply:
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

        self._llm_log_func(str(MessageType.AI), reply)
        return reply if format is None else format.model_validate_json(reply)
