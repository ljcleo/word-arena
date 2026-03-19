from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from .base import BaseManualReader


class BaseInputManualReader[GT](BaseManualReader[GT], ABC):
    def __init__(self, *, input_func: Callable[[str], str]) -> None:
        self._input_func: Callable[[str], str] = input_func

    @override
    def read_guess(self, *, turn_id: int) -> GT:
        return self.input_guess(turn_id=turn_id, input_func=self._input_func)

    @abstractmethod
    def input_guess(self, *, turn_id: int, input_func: Callable[[str], str]) -> GT: ...
