from abc import ABC, abstractmethod

from ....common.game.common import Trajectory


class BaseManualReader[IT, GT, FT](ABC):
    @abstractmethod
    def read_guess(self, *, trajectory: Trajectory[IT, GT, FT]) -> GT: ...
