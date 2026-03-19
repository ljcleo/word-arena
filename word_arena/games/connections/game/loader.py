from random import Random
from typing import override

from pydantic import TypeAdapter

from ....common.game.loader.base import BaseGameLoader
from ....utils import create_seed, get_db_cursor
from ..common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo
from .common import ConnectionsConfig
from .engine import ConnectionsGameEngine


class ConnectionsGameLoader(
    BaseGameLoader[
        ConnectionsConfig,
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
    ]
):
    @override
    def create_engine(self, *, config: ConnectionsConfig) -> ConnectionsGameEngine:
        with get_db_cursor(data_file=config.data_file) as cur:
            groups: dict[str, list[str]] = TypeAdapter(dict[str, list[str]]).validate_json(
                cur.execute(
                    "SELECT groups FROM game WHERE game_id = ?", (config.game_id,)
                ).fetchone()[0]
            )

        words: list[str] = sum(groups.values(), [])
        Random(create_seed(data="/".join(words))).shuffle(words)

        return ConnectionsGameEngine(
            words=words,
            groups={theme: list(map(words.index, group)) for theme, group in groups.items()},
            max_turns=config.max_turns,
        )
