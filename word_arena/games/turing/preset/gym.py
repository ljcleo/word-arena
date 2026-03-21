from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import TuringConfig, TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ..config.common import TuringMetaConfig, TuringMutableMetaConfig
from ..config.generator import TuringConfigGenerator
from ..config.reader.input import TuringInputConfigReader
from ..game.engine import TuringGameEngine
from ..game.renderer.log import TuringLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [
        TuringMetaConfig,
        Sequence[TuringMutableMetaConfig],
        Callable[[str], str],
        Callable[[str, str], None],
    ],
    Gym[
        TuringMetaConfig,
        TuringMutableMetaConfig,
        TuringConfig,
        TuringInfo,
        TuringGuess,
        TuringFeedback,
        TuringFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=TuringInputConfigReader,
    config_generator_cls=TuringConfigGenerator,
    game_engine_cls=TuringGameEngine,
    log_game_renderer_cls=TuringLogGameRenderer,
)
