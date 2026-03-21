from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import ConexoConfig, ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..config.common import ConexoMetaConfig
from ..config.generator import ConexoConfigGenerator
from ..config.reader.input import ConexoInputConfigReader
from ..game.engine import ConexoGameEngine
from ..game.renderer.log import ConexoLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [ConexoMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        ConexoMetaConfig,
        int,
        ConexoConfig,
        ConexoInfo,
        ConexoGuess,
        ConexoFeedback,
        ConexoFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=ConexoInputConfigReader,
    config_generator_cls=ConexoConfigGenerator,
    game_engine_cls=ConexoGameEngine,
    log_game_renderer_cls=ConexoLogGameRenderer,
)
