from collections.abc import Callable
from typing import override

from ..common import MessageType
from .base import BaseLLMRenderer


class LogLLMRenderer(BaseLLMRenderer):
    def __init__(self, *, llm_log_func: Callable[[str, str], None]) -> None:
        self._llm_log_func: Callable[[str, str], None] = llm_log_func

    @override
    def render_message(self, *, message_type: MessageType | str, content: str) -> None:
        self._llm_log_func(
            "HUMAN"
            if message_type == MessageType.HUMAN
            else "AI"
            if message_type == MessageType.AI
            else message_type,
            content,
        )
