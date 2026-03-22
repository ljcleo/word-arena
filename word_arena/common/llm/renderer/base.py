from abc import ABC, abstractmethod

from ..common import MessageType


class BaseLLMRenderer(ABC):
    @abstractmethod
    def render_message(self, *, message_type: MessageType | str, content: str) -> None: ...
