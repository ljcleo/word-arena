from abc import ABC, abstractmethod
from typing import override

from ..game.base import BaseGame
from ..generator.provider import BaseGameProvider
from ..player.manual import BaseManualPlayer
from .base import BaseConfigGym


class BaseManualGym[CT, IT, HT, GT, FT, RT](BaseConfigGym[CT, IT, HT, GT, FT, RT, []], ABC):
    def __init__(
        self, *, game_provider: BaseGameProvider[CT, BaseGame[IT, HT, GT, FT, RT]]
    ) -> None:
        self._game_provider: BaseGameProvider[CT, BaseGame[IT, HT, GT, FT, RT]] = game_provider

    @override
    def create_player_with_cb(self) -> tuple[BaseManualPlayer[IT, HT, GT, FT], None, None]:
        return self.create_player(), None, None

    @override
    def create_game_from_config(self, *, config: CT) -> BaseGame[IT, HT, GT, FT, RT]:
        return self._game_provider.create_game(config=config)

    @abstractmethod
    def create_player(self) -> BaseManualPlayer[IT, HT, GT, FT]:
        raise NotImplementedError()
