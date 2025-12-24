from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import ConexoGame
from .common import ConexoConfig, ConexoGameData


class ConexoGameProvider(BaseGameProvider[Path, ConexoConfig, ConexoGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=data_file, **kwargs)

    @override
    def create_game(self, *, meta_config: Path, config: ConexoConfig) -> ConexoGame:
        con: Connection = connect(meta_config)
        cur: Cursor = con.cursor()

        try:
            with con:
                game_data: ConexoGameData = ConexoGameData.model_validate_json(
                    cur.execute(
                        "SELECT game_data FROM game WHERE game_id = ?", (config.game_id,)
                    ).fetchone()[0]
                )
        finally:
            con.close()

        return ConexoGame(
            words=game_data.words,
            groups={group.theme: group.indices for group in game_data.groups},
            max_guesses=config.max_guesses,
        )
