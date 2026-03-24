from abc import ABC, abstractmethod

from ..state import ManualGameStateInterface


class BaseManualReader[IT, GT, FT](ABC):
    @abstractmethod
    def read_guess(self, *, game_state: ManualGameStateInterface[IT, GT, FT]) -> GT: ...
