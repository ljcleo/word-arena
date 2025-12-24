from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import override

from pydantic import TypeAdapter

from ....common.generator.provider import BaseGameProvider
from ..game import ContextoHintGame
from .common import ContextoHintConfig


class ContextoHintGameProvider(BaseGameProvider[Path, ContextoHintConfig, ContextoHintGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=data_file, **kwargs)

    @override
    def create_game(self, *, meta_config: Path, config: ContextoHintConfig) -> ContextoHintGame:
        con: Connection = connect(meta_config)
        cur: Cursor = con.cursor()

        try:
            with con:
                return ContextoHintGame(
                    top_words=TypeAdapter(list[str]).validate_json(
                        cur.execute(
                            "SELECT top_words FROM game WHERE game_id = ?", (config.game_id,)
                        ).fetchone()[0]
                    ),
                    num_candidates=config.num_candidates,
                )
        finally:
            con.close()
