from abc import ABC, abstractmethod


class BaseManualReader[GT](ABC):
    @abstractmethod
    def read_guess(self, *, turn_id: int) -> GT: ...
