from collections.abc import Iterable
from datetime import date
from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ContextoGame
from .common import ContextoConfig, ContextoSetting
from .provider import ContextoGameProvider


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
