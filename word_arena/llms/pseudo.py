from typing import override

from pydantic import BaseModel

from ..common.llm.base import BaseLLM
from ..common.llm.common import Message, MessageType


class PseudoLLM(BaseLLM):
    @override
    def query(self, *messages: Message) -> str:
        for message in messages:
            print(f"[[{message.role}]]\n--------\n{message.content}\n--------\n")

        print(f"[[{MessageType.AI}]] (Input Manually Below)")
        return input()

    @override
    def parse[T: BaseModel](self, *messages: Message, format: type[T]) -> T:
        for message in messages:
            print(f"[[{message.role}]]\n--------\n{message.content}\n--------\n")

        print(f"[[{MessageType.AI}]] (Input Manually Below)")
        return format.model_validate_json(input())
