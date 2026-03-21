from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import LetrosoConfig, LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..config.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..config.generator import LetrosoConfigGenerator
from ..config.reader.input import LetrosoInputConfigReader
from ..game.engine import LetrosoGameEngine
from ..game.renderer.log import LetrosoLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [
        LetrosoMetaConfig,
        Sequence[LetrosoMutableMetaConfig],
        Callable[[str], str],
        Callable[[str, str], None],
    ],
    Gym[
        LetrosoMetaConfig,
        LetrosoMutableMetaConfig,
        LetrosoConfig,
        LetrosoInfo,
        LetrosoGuess,
        LetrosoFeedback,
        LetrosoFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=LetrosoInputConfigReader,
    config_generator_cls=LetrosoConfigGenerator,
    game_engine_cls=LetrosoGameEngine,
    log_game_renderer_cls=LetrosoLogGameRenderer,
)
