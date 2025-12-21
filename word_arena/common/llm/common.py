from __future__ import annotations

import enum

from pydantic import BaseModel


@enum.unique
class MessageType(enum.Enum):
    SYSTEM = enum.auto()
    HUMAN = enum.auto()
    AI = enum.auto()


class Message(BaseModel):
    role: MessageType
    content: str

    @staticmethod
    def system(*sections: str) -> Message:
        return Message(role=MessageType.SYSTEM, content="\n\n".join(sections))

    @staticmethod
    def human(*sections: str) -> Message:
        return Message(role=MessageType.HUMAN, content="\n\n".join(sections))

    @staticmethod
    def ai(*sections: str) -> Message:
        return Message(role=MessageType.AI, content="\n\n".join(sections))
