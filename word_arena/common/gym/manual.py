from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from ..game.base import BaseGame
from ..generator.provider import BaseGameProvider
from ..player.manual import BaseManualPlayer
from .base import BaseConfigGym


class BaseManualGym[MT, CT, IT, HT, GT, FT, RT](
    BaseConfigGym[CT, IT, HT, GT, FT, RT, [Callable[[str], str], Callable[[str], None]]], ABC
):
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        game_provider: BaseGameProvider[MT, CT, BaseGame[IT, HT, GT, FT, RT]],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._game_provider: BaseGameProvider[MT, CT, BaseGame[IT, HT, GT, FT, RT]] = game_provider

    @override
    def create_player_with_cb(
        self, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> tuple[BaseManualPlayer[IT, HT, GT, FT], None, None]:
        return (
            self.create_player(input_func=input_func, player_log_func=player_log_func),
            None,
            None,
        )

    @override
    def create_game_from_config(self, *, config: CT) -> BaseGame[IT, HT, GT, FT, RT]:
        return self._game_provider.create_game_from_config(config=config)

    @abstractmethod
    def create_player(
        self, *, input_func: Callable[[str], str], player_log_func: Callable[[str], None]
    ) -> BaseManualPlayer[IT, HT, GT, FT]:
        raise NotImplementedError()
