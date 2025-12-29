from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import StrandsGame
from .common import StrandsConfig, StrandsGameData


class StrandsGameProvider(BaseGameProvider[Path, StrandsConfig, StrandsGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=data_file, **kwargs)

    @override
    def create_game(self, *, meta_config: Path, config: StrandsConfig) -> StrandsGame:
        con: Connection = connect(meta_config)
        cur: Cursor = con.cursor()

        try:
            with con:
                data: StrandsGameData = StrandsGameData.model_validate_json(
                    cur.execute(
                        "SELECT board FROM game WHERE game_id = ?", (config.game_id,)
                    ).fetchone()[0]
                )
        finally:
            con.close()

        return StrandsGame(board=data.board, clue=data.clue, max_guesses=config.max_guesses)
