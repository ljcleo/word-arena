from random import Random
from typing import override

from pydantic import TypeAdapter

from ....common.game.loader.base import BaseGameLoader
from ....utils import create_seed, get_db_cursor
from ..common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from .common import ConexoConfig
from .engine import ConexoGameEngine


class ConexoGameLoader(
    BaseGameLoader[ConexoConfig, ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult]
):
    @override
    def create_engine(self, *, config: ConexoConfig) -> ConexoGameEngine:
        with get_db_cursor(data_file=config.data_file) as cur:
            groups: dict[str, list[str]] = TypeAdapter(dict[str, list[str]]).validate_json(
                cur.execute(
                    "SELECT groups FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        words: list[str] = sum(groups.values(), [])
        Random(create_seed(data="/".join(words))).shuffle(words)

        return ConexoGameEngine(
            words=words,
            groups={theme: list(map(words.index, group)) for theme, group in groups.items()},
            max_turns=config.max_turns,
        )
