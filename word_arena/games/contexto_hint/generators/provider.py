from typing import override

from pydantic import TypeAdapter

from ....common.generator.provider import BaseGameProvider
from ....common.utils import get_db_cursor
from ..game import ContextoHintGame
from .common import ContextoHintConfig, ContextoHintMetaConfig


class ContextoHintGameProvider(
    BaseGameProvider[ContextoHintMetaConfig, ContextoHintConfig, ContextoHintGame]
):
    @override
    def create_game(
        self, *, meta_config: ContextoHintMetaConfig, config: ContextoHintConfig
    ) -> ContextoHintGame:
        with get_db_cursor(data_file=meta_config.data_file) as cur:
            return ContextoHintGame(
                top_words=TypeAdapter(list[str]).validate_json(
                    cur.execute(
                        "SELECT top_words FROM game WHERE game_id = ?", (config.game_id,)
                    ).fetchone()[0]
                ),
                num_candidates=config.num_candidates,
            )
