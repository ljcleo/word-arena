from collections.abc import Iterable
from pathlib import Path
from random import Random
from typing import override

from pydantic import BaseModel

from ...common.game.generator import BaseGameGenerator, BaseGameProvider
from .game import ConexoGame


class ConexoSetting(BaseModel):
    max_guesses: int


class ConexoConfig(BaseModel):
    game_id: int
    max_guesses: int


class ConexoGroupData(BaseModel):
    indices: list[int]
    theme: str


class ConexoGameData(BaseModel):
    id: int
    words: list[str]
    groups: list[ConexoGroupData]


class ConexoGameProvider(BaseGameProvider[ConexoConfig, ConexoGame]):
    def __init__(self, *, games_dir: Path) -> None:
        self._games_dir: Path = games_dir

    @override
    def create_game(self, *, config: ConexoConfig) -> ConexoGame:
        with (self._games_dir / f"{config.game_id}.json").open("rb") as f:
            game_data: ConexoGameData = ConexoGameData.model_validate_json(f.read())

        return ConexoGame(
            words=game_data.words,
            groups={group.theme: group.indices for group in game_data.groups},
            max_guesses=config.max_guesses,
        )


class ConexoGameGenerator(
    BaseGameGenerator[ConexoSetting, ConexoConfig, ConexoGame], ConexoGameProvider
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[ConexoSetting], seed: int, games_dir: Path
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        super(BaseGameGenerator).__init__(games_dir=games_dir)
        self._num_games: int = sum(1 for _ in games_dir.iterdir())

    @override
    def generate_config(self, *, setting: ConexoSetting, rng: Random) -> ConexoConfig:
        return ConexoConfig(game_id=rng.randrange(self._num_games), max_guesses=setting.max_guesses)
