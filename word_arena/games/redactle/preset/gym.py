from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import (
    RedactleConfig,
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
)
from ..config.common import RedactleMetaConfig
from ..config.generator import RedactleConfigGenerator
from ..config.reader.input import RedactleInputConfigReader
from ..game.engine import RedactleGameEngine
from ..game.renderer.log import RedactleLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [RedactleMetaConfig, Sequence[int], Callable[[str], str], Callable[[str, str], None]],
    Gym[
        RedactleMetaConfig,
        int,
        RedactleConfig,
        RedactleInfo,
        RedactleGuess,
        RedactleFeedback,
        RedactleFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=RedactleInputConfigReader,
    config_generator_cls=RedactleConfigGenerator,
    game_engine_cls=RedactleGameEngine,
    log_game_renderer_cls=RedactleLogGameRenderer,
)
