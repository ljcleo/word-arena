from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import (
    NumberleConfig,
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
)
from ..config.common import NumberleMetaConfig, NumberleMutableMetaConfig
from ..config.generator import NumberleConfigGenerator
from ..config.reader.input import NumberleInputConfigReader
from ..game.engine import NumberleGameEngine
from ..game.renderer.log import NumberleLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [
        NumberleMetaConfig,
        Sequence[NumberleMutableMetaConfig],
        Callable[[str], str],
        Callable[[str, str], None],
    ],
    Gym[
        NumberleMetaConfig,
        NumberleMutableMetaConfig,
        NumberleConfig,
        NumberleInfo,
        NumberleGuess,
        NumberleFeedback,
        NumberleFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=NumberleInputConfigReader,
    config_generator_cls=NumberleConfigGenerator,
    game_engine_cls=NumberleGameEngine,
    log_game_renderer_cls=NumberleLogGameRenderer,
)
