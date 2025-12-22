from collections.abc import Iterable
from pathlib import Path
from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ContextoHintGame
from .common import ContextoHintConfig, ContextoHintSetting
from .provider import ContextoHintGameProvider


class ContextoHintGameGenerator(
    BaseGameGenerator[ContextoHintSetting, ContextoHintConfig, ContextoHintGame],
    ContextoHintGameProvider,
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[ContextoHintSetting], seed: int, games_dir: Path
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        super(BaseGameGenerator).__init__(games_dir=games_dir)
        self._num_games: int = sum(1 for _ in games_dir.iterdir())

    @override
    def generate_config(self, *, setting: ContextoHintSetting, rng: Random) -> ContextoHintConfig:
        return ContextoHintConfig(
            game_id=rng.randrange(self._num_games), num_candidates=setting.num_candidates
        )
