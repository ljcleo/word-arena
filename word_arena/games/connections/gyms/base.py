from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo
from ..formatters.base import ConnectionsFinalResultFormatter
from ..generators.common import ConnectionsConfig, get_connections_game_count


class ConnectionsConfigGym[**P](
    BaseConfigGym[
        Path,
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
    def create_config(self, *, meta_config: Path) -> ConnectionsConfig:
        return ConnectionsConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_id=int(
                self._input_func(
                    f"Game ID (0--{get_connections_game_count(data_file=meta_config) - 1}): "
                )
            ),
        )
