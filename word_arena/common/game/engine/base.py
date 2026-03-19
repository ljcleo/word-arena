from abc import ABC, abstractmethod

from ..state import GameStateInterface


class BaseGameEngine[IT, GT, FT, RT](ABC):
    @abstractmethod
    def start_game(self) -> IT: ...

    @abstractmethod
    def is_over(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> bool: ...

    @abstractmethod
    def process_guess(self, *, guess: GT) -> FT: ...

    @abstractmethod
    def get_final_result(self) -> RT: ...
