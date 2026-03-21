from random import Random
from typing import override

from ....common.config.generator.base import BaseConfigGenerator
from ..common import ConnectionsConfig
from .common import ConnectionsMetaConfig


class ConnectionsConfigGenerator(
    BaseConfigGenerator[ConnectionsMetaConfig, int, ConnectionsConfig]
):
    @override
    def __call__(
        self, *, meta_config: ConnectionsMetaConfig, mutable_meta_config: int, rng: Random
    ) -> ConnectionsConfig:
        return ConnectionsConfig(
            data_file=meta_config.data_file,
            max_turns=mutable_meta_config,
            game_id=meta_config.random_game_id(rng=rng),
        )
