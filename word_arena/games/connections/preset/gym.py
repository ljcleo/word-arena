from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import (
    ConnectionsConfig,
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
)
from ..config.common import ConnectionsMetaConfig
from ..config.generator import ConnectionsConfigGenerator
from ..config.reader.input import ConnectionsInputConfigReader
from ..game.engine import ConnectionsGameEngine
from ..game.renderer.log import ConnectionsLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [ConnectionsMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        ConnectionsMetaConfig,
        int,
        ConnectionsConfig,
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=ConnectionsInputConfigReader,
    config_generator_cls=ConnectionsConfigGenerator,
    game_engine_cls=ConnectionsGameEngine,
    log_game_renderer_cls=ConnectionsLogGameRenderer,
)
