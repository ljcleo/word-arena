from collections.abc import Callable
from typing import override

from .....common.config.selector.input import BaseInputConfigSelector
from ...common import ConnectionsConfig
from ..common import ConnectionsMetaConfig


class ConnectionsInputConfigSelector(
    BaseInputConfigSelector[ConnectionsMetaConfig, ConnectionsConfig]
):
    @override
    def input_config(
        self, *, meta_config: ConnectionsMetaConfig, input_func: Callable[[str], str]
    ) -> ConnectionsConfig:
        return ConnectionsConfig(
            data_file=meta_config.data_file,
            max_turns=int(input_func("Max Turns: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(input_func(f"Game ID (0--{n - 1}): "))
            ),
        )
