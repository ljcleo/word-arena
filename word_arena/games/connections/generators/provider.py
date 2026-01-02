from random import Random
from typing import override

from pydantic import TypeAdapter

from ....common.generator.provider import BaseGameProvider
from ....common.utils import create_seed, get_db_cursor
from ..game import ConnectionsGame
from .common import ConnectionsConfig, ConnectionsMetaConfig


class ConnectionsGameProvider(
    BaseGameProvider[ConnectionsMetaConfig, ConnectionsConfig, ConnectionsGame]
):
    @override
    def create_game(
        self, *, meta_config: ConnectionsMetaConfig, config: ConnectionsConfig
    ) -> ConnectionsGame:
        with get_db_cursor(data_file=meta_config.data_file) as cur:
            groups: dict[str, list[str]] = TypeAdapter(dict[str, list[str]]).validate_json(
                cur.execute(
                    "SELECT groups FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        words: list[str] = sum(groups.values(), [])
        Random(create_seed(data="/".join(words))).shuffle(words)

        return ConnectionsGame(
            words=words,
            groups={theme: list(map(words.index, group)) for theme, group in groups.items()},
            max_guesses=config.max_guesses,
        )
