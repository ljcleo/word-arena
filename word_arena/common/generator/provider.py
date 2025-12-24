from abc import ABC, abstractmethod

from ..game.base import BaseGame


class BaseGameProvider[MT, CT, GT: BaseGame](ABC):
    def __init__(self, *, meta_config: MT, **kwargs):
        super().__init__(**kwargs)
        self._meta_config: MT = meta_config

    @property
    def meta_config(self) -> MT:
        return self._meta_config

    def create_game_from_config(self, *, config: CT) -> GT:
        return self.create_game(meta_config=self.meta_config, config=config)

    @abstractmethod
    def create_game(self, *, meta_config: MT, config: CT) -> GT:
        raise NotImplementedError
