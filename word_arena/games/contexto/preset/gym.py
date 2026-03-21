from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import ContextoConfig, ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..config.common import ContextoMetaConfig
from ..config.generator import ContextoConfigGenerator
from ..config.reader.input import ContextoInputConfigReader
from ..game.engine import ContextoGameEngine
from ..game.renderer.log import ContextoLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [ContextoMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        ContextoMetaConfig,
        int,
        ContextoConfig,
        int,
        ContextoGuess,
        ContextoFeedback,
        ContextoFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=ContextoInputConfigReader,
    config_generator_cls=ContextoConfigGenerator,
    game_engine_cls=ContextoGameEngine,
    log_game_renderer_cls=ContextoLogGameRenderer,
)
