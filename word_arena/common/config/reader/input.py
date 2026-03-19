from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from .base import BaseConfigReader


class BaseInputConfigReader[MT, CT](BaseConfigReader[MT, CT], ABC):
    def __init__(self, *, input_func: Callable[[str], str]) -> None:
        self._input_func: Callable[[str], str] = input_func

    @override
    def read_config(self, *, meta_config: MT) -> CT:
        return self.input_config(input_func=self._input_func, meta_config=meta_config)

    @abstractmethod
    def input_config(self, *, meta_config: MT, input_func: Callable[[str], str]) -> CT: ...
