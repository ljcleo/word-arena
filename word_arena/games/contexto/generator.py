from collections.abc import Iterable
from datetime import date
from random import Random
from typing import override

from pydantic import BaseModel

from ...common.game.generator import BaseGameGenerator, BaseGameProvider
from .game import ContextoGame


class ContextoSetting(BaseModel):
    max_guesses: int


class ContextoConfig(BaseModel):
    game_id: int
    max_guesses: int


class ContextoGameProvider(BaseGameProvider[ContextoConfig, ContextoGame]):
    @override
    def create_game(self, *, config: ContextoConfig) -> ContextoGame:
        return ContextoGame(game_id=config.game_id, max_guesses=config.max_guesses)


class ContextoGameGenerator(
    BaseGameGenerator[ContextoSetting, ContextoConfig, ContextoGame], ContextoGameProvider
):
    @override
    def __init__(self, *, setting_pool: Iterable[ContextoSetting], seed: int) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        self._num_games: int = (date.today() - date(2022, 9, 18)).days + 1

    @override
    def generate_config(self, *, setting: ContextoSetting, rng: Random) -> ContextoConfig:
        return ContextoConfig(
            game_id=rng.randrange(self._num_games), max_guesses=setting.max_guesses
        )
