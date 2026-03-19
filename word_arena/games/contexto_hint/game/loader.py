from typing import override

from pydantic import TypeAdapter

from ....common.game.loader.base import BaseGameLoader
from ....utils import get_db_cursor
from ..common import ContextoHintFeedback, ContextoHintGuess
from .common import ContextoHintConfig
from .engine import ContextoHintGameEngine


class ContextoHintGameLoader(
    BaseGameLoader[
        ContextoHintConfig, list[str], ContextoHintGuess, ContextoHintFeedback, list[str]
    ]
):
    @override
    def create_engine(self, *, config: ContextoHintConfig) -> ContextoHintGameEngine:
        with get_db_cursor(data_file=config.data_file) as cur:
            return ContextoHintGameEngine(
                top_words=TypeAdapter(list[str]).validate_json(
                    cur.execute(
                        "SELECT top_words FROM game WHERE game_id = ?", (config.game_id,)
                    ).fetchone()[0]
                ),
                num_candidates=config.num_candidates,
            )
