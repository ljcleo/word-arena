from abc import ABC, abstractmethod

from ..game.base import BaseGame


class BaseGameProvider[CT, GT: BaseGame](ABC):
    @abstractmethod
    def create_game(self, *, config: CT) -> GT:
        raise NotImplementedError
