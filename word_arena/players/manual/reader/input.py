from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from ....common.game.common import Trajectory
from .base import BaseManualReader


class BaseInputManualReader[PT, IT, GT, FT](BaseManualReader[IT, GT, FT], ABC):
    def __init__(self, *, input_func: Callable[[str], str], prompt_config: PT) -> None:
        self._input_func: Callable[[str], str] = input_func
        self._prompt_config: PT = prompt_config

    @property
    def prompt_config(self) -> PT:
        return self._prompt_config

    @override
    def read_guess(self, *, trajectory: Trajectory[IT, GT, FT]) -> GT:
        return self.input_guess(trajectory=trajectory, input_func=self._input_func)

    @abstractmethod
    def input_guess(
        self, *, trajectory: Trajectory[IT, GT, FT], input_func: Callable[[str], str]
    ) -> GT: ...
