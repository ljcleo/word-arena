from pathlib import Path
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import ContextoHintGame
from .common import ContextoHintConfig


class ContextoHintGameProvider(BaseGameProvider[ContextoHintConfig, ContextoHintGame]):
    def __init__(self, *, games_dir: Path) -> None:
        self._games_dir: Path = games_dir

    @override
    def create_game(self, *, config: ContextoHintConfig) -> ContextoHintGame:
        return ContextoHintGame(
            top_words=(self._games_dir / f"{config.game_id}.txt").read_text().strip().split(),
            num_candidates=config.num_candidates,
        )
