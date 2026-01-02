from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import ConnectionsGame
from .common import ConnectionsConfig, ConnectionsMetaConfig
from .provider import ConnectionsGameProvider


class ConnectionsGameGenerator(
    ConnectionsGameProvider,
    BaseGameGenerator[ConnectionsMetaConfig, int, ConnectionsConfig, ConnectionsGame],
):
    @override
    def generate_config(
        self, *, meta_config: ConnectionsMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ConnectionsConfig:
        return ConnectionsConfig(
            max_guesses=mutable_meta_config, game_id=meta_config.random_game_id(rng=rng)
        )
