from abc import ABC, abstractmethod

from ..engine.base import BaseGameEngine
from ..game import Game
from ..renderer.base import BaseGameRenderer


class BaseGameLoader[CT, IT, GT, FT, RT](ABC):
    def __init__(self, *, renderer: BaseGameRenderer[IT, GT, FT, RT]) -> None:
        self._renderer: BaseGameRenderer[IT, GT, FT, RT] = renderer

    def load_game(self, *, config: CT) -> Game[IT, GT, FT, RT]:
        return Game(engine=self.create_engine(config=config), renderer=self._renderer)

    @abstractmethod
    def create_engine(self, *, config: CT) -> BaseGameEngine[IT, GT, FT, RT]: ...
