from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import ContextoHintConfig, ContextoHintFeedback, ContextoHintGuess
from ..config.common import ContextoHintMetaConfig
from ..config.generator import ContextoHintConfigGenerator
from ..config.reader.input import ContextoHintInputConfigReader
from ..game.engine import ContextoHintGameEngine
from ..game.renderer.log import ContextoHintLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [ContextoHintMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        ContextoHintMetaConfig,
        int,
        ContextoHintConfig,
        list[str],
        ContextoHintGuess,
        ContextoHintFeedback,
        list[str],
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=ContextoHintInputConfigReader,
    config_generator_cls=ContextoHintConfigGenerator,
    game_engine_cls=ContextoHintGameEngine,
    log_game_renderer_cls=ContextoHintLogGameRenderer,
)
