from hashlib import sha256
from pathlib import Path
from random import Random
from sqlite3 import Connection, Cursor, connect
from typing import override

from pydantic import TypeAdapter

from ....common.generator.provider import BaseGameProvider
from ..game import ConexoGame
from .common import ConexoConfig


class ConexoGameProvider(BaseGameProvider[Path, ConexoConfig, ConexoGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=data_file, **kwargs)

    @override
    def create_game(self, *, meta_config: Path, config: ConexoConfig) -> ConexoGame:
        con: Connection = connect(meta_config)
        cur: Cursor = con.cursor()

        try:
            with con:
                groups: dict[str, list[str]] = TypeAdapter(dict[str, list[str]]).validate_json(
                    cur.execute(
                        "SELECT groups FROM game WHERE game_id = ?", (config.game_id,)
                    ).fetchone()[0]
                )
        finally:
            con.close()

        words: list[str] = sum(groups.values(), [])

        Random(
            int(sha256("/".join(words).encode(encoding="utf8")).hexdigest(), base=16)
            & ((1 << 32) - 1)
        ).shuffle(words)

        return ConexoGame(
            words=words,
            groups={theme: list(map(words.index, group)) for theme, group in groups.items()},
            max_guesses=config.max_guesses,
        )
