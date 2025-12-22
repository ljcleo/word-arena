from pathlib import Path
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import ConexoGame
from .common import ConexoConfig, ConexoGameData


class ConexoGameProvider(BaseGameProvider[ConexoConfig, ConexoGame]):
    def __init__(self, *, games_dir: Path, **kwargs) -> None:
        super().__init__(**kwargs)
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
