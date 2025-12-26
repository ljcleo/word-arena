from typing import override

from pydantic import BaseModel

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


class PseudoLLM(BaseLLM):
    def __init__(self, *, auto_reply: bool) -> None:
        self._auto_reply: bool = auto_reply

    @override
    def query(self, *messages: Message) -> str:
        return self._query(*messages, is_parse=False)

    @override
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        return format.model_validate_json(self._query(*messages, is_parse=True))

    def _query(self, *messages: Message, is_parse: bool) -> str:
        for message in messages:
            print(f"[[{message.role}]]\n--------\n{message.content}\n--------\n")

        if self._auto_reply:
            reply: str = (
                messages[-1]
                .content.rsplit("\n", maxsplit=1)[-1]
                .partition("`")[2]
                .partition("`")[0]
                if is_parse
                else "This is an auto reply."
            )
            print(f"[[{MessageType.AI}]]\n{reply}")
            return reply
        else:
            print(f"[[{MessageType.AI}]] (Input Manually Below)")
            return input().strip()
