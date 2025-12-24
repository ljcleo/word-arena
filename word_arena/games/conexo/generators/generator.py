from pathlib import Path
from random import Random
from sqlite3 import Connection, Cursor, connect
from typing import Iterable, override

from ....common.generator.generator import BaseGameGenerator
from ..game import ConexoGame
from .common import ConexoConfig
from .provider import ConexoGameProvider


class ConexoGameGenerator(
    ConexoGameProvider, BaseGameGenerator[Path, int, ConexoConfig, ConexoGame]
):
    def __init__(
        self, *, data_file: Path, mutable_meta_config_pool: Iterable[int], seed: int, **kwargs
    ) -> None:
        super().__init__(
            data_file=data_file,
            mutable_meta_config_pool=mutable_meta_config_pool,
            seed=seed,
            **kwargs,
        )

    @override
    def generate_config(
        self, *, meta_config: Path, mutable_meta_config: int, rng: Random
    ) -> ConexoConfig:
        con: Connection = connect(meta_config)
        cur: Cursor = con.cursor()

        try:
            with con:
                return ConexoConfig(
                    max_guesses=mutable_meta_config,
                    game_id=rng.randrange(cur.execute("SELECT COUNT(*) FROM game").fetchone()[0]),
                )
        finally:
            con.close()
