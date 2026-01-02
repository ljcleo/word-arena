from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo
from ..formatters.base import ConnectionsFinalResultFormatter
from ..generators.common import ConnectionsConfig, ConnectionsMetaConfig


class ConnectionsConfigGym[**P](
    BaseConfigGym[
        ConnectionsMetaConfig,
        ConnectionsConfig,
        ConnectionsInfo,
        None,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        P,
    ],
    ConnectionsFinalResultFormatter,
):
    pass


class ConnectionsExampleConfigGym(ConnectionsConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: ConnectionsMetaConfig) -> ConnectionsConfig:
        return ConnectionsConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=meta_config.select_game_id(
                selector=lambda n: int(self._input_func(f"Game ID (0--{n - 1}): "))
            ),
        )
