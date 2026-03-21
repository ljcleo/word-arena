from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import StrandsConfig, StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ..config.common import StrandsMetaConfig
from ..config.generator import StrandsConfigGenerator
from ..config.reader.input import StrandsInputConfigReader
from ..game.engine import StrandsGameEngine
from ..game.renderer.log import StrandsLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [StrandsMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        StrandsMetaConfig,
        int,
        StrandsConfig,
        StrandsInfo,
        StrandsGuess,
        StrandsFeedback,
        StrandsFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=StrandsInputConfigReader,
    config_generator_cls=StrandsConfigGenerator,
    game_engine_cls=StrandsGameEngine,
    log_game_renderer_cls=StrandsLogGameRenderer,
)
