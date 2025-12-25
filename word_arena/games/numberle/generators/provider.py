from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import NumberleGame
from .common import NumberleConfig, NumberleMetaConfig


class NumberleGameProvider(BaseGameProvider[NumberleMetaConfig, NumberleConfig, NumberleGame]):
    def __init__(self, *, data_file: Path, **kwargs):
        super().__init__(meta_config=self._load_meta_config(data_file=data_file), **kwargs)

    @override
    def create_game(
        self, *, meta_config: NumberleMetaConfig, config: NumberleConfig
    ) -> NumberleGame:
        return NumberleGame(
            eq_list=meta_config.eq_list,
            target_ids=[
                meta_config.target_pool[config.eq_length][index] for index in config.game_ids
            ],
            eq_length=config.eq_length,
            max_guesses=config.max_guesses,
        )

    @staticmethod
    def _load_meta_config(*, data_file: Path) -> NumberleMetaConfig:
        con: Connection = connect(data_file)
        cur: Cursor = con.cursor()

        try:
            with con:
                eq_data: dict[int, str] = dict(cur.execute("SELECT eq_id, eq FROM eq"))

            game_data: dict[int, dict[int, int]] = {}

            for eq_length in range(5, 13):
                with con:
                    game_data[eq_length] = dict(
                        cur.execute(f"SELECT game_id, eq_id FROM game_{eq_length}")
                    )
        finally:
            con.close()

        return NumberleMetaConfig(
            eq_list=[eq_data[i] for i in range(len(eq_data))],
            target_pool={
                eq_length: [sub_game_data[i] for i in range(len(sub_game_data))]
                for eq_length, sub_game_data in game_data.items()
            },
        )
