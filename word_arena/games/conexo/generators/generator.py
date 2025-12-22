from collections.abc import Iterable
from pathlib import Path
from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ConexoGame
from .common import ConexoConfig, ConexoSetting
from .provider import ConexoGameProvider


class ConexoGameGenerator(
    BaseGameGenerator[ConexoSetting, ConexoConfig, ConexoGame], ConexoGameProvider
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[ConexoSetting], seed: int, games_dir: Path
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        super(BaseGameGenerator, self).__init__(games_dir=games_dir)
        self._num_games: int = sum(1 for _ in games_dir.iterdir())

    @override
    def generate_config(self, *, setting: ConexoSetting, rng: Random) -> ConexoConfig:
        return ConexoConfig(game_id=rng.randrange(self._num_games), max_guesses=setting.max_guesses)
