from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import LetrosoGame
from .common import LetrosoConfig, LetrosoMetaConfig


class LetrosoGameProvider(BaseGameProvider[LetrosoMetaConfig, LetrosoConfig, LetrosoGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=self._load_meta_config(data_file=data_file), **kwargs)

    @override
    def create_game(self, *, meta_config: LetrosoMetaConfig, config: LetrosoConfig) -> LetrosoGame:
        return LetrosoGame(
            word_list=meta_config.word_list,
            target_ids=[meta_config.target_pool[index] for index in config.game_ids],
            max_letters=config.max_letters,
            max_guesses=config.max_guesses,
        )

    @staticmethod
    def _load_meta_config(*, data_file: Path) -> LetrosoMetaConfig:
        con: Connection = connect(data_file)
        cur: Cursor = con.cursor()

        try:
            with con:
                word_data: dict[int, str] = dict(cur.execute("SELECT word_id, word FROM word"))
        finally:
            con.close()

        word_list: list[str] = [word_data[i] for i in range(len(word_data))]
        return LetrosoMetaConfig(word_list=word_list, target_pool=list(range(len(word_list))))
