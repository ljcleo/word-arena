from abc import ABC, abstractmethod

from ..state import GameStateInterface


class BaseGameRenderer[IT, GT, FT, RT](ABC):
    @abstractmethod
    def render_game_info(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None: ...

    @abstractmethod
    def render_guess(self, *, state: GameStateInterface[IT, GT, FT, RT], guess: GT) -> None: ...

    @abstractmethod
    def render_last_feedback(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None: ...

    @abstractmethod
    def render_final_result(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None: ...
