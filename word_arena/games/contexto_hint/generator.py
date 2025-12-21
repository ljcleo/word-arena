from collections.abc import Iterable
from pathlib import Path
from random import Random
from typing import override

from pydantic import BaseModel

from ...common.game.generator import BaseGameGenerator, BaseGameProvider
from .game import ContextoHintGame


class ContextoHintSetting(BaseModel):
    num_candidates: int


class ContextoHintConfig(BaseModel):
    game_id: int
    num_candidates: int


class ContextoHintGameProvider(BaseGameProvider[ContextoHintConfig, ContextoHintGame]):
    def __init__(self, *, games_dir: Path) -> None:
        self._games_dir: Path = games_dir

    @override
    def create_game(self, *, config: ContextoHintConfig) -> ContextoHintGame:
        return ContextoHintGame(
            top_words=(self._games_dir / f"{config.game_id}.txt").read_text().strip().split(),
            num_candidates=config.num_candidates,
        )


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
