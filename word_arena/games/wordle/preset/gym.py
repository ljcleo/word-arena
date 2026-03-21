from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import make_input_config_reader_log_game_renderer
from ..common import WordleConfig, WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..config.common import WordleMetaConfig, WordleMutableMetaConfig
from ..config.generator import WordleConfigGenerator
from ..config.reader.input import WordleInputConfigReader
from ..game.engine import WordleGameEngine
from ..game.renderer.log import WordleLogGameRenderer

input_config_reader_log_game_renderer: Callable[
    [
        WordleMetaConfig,
        Sequence[WordleMutableMetaConfig],
        Callable[[str], str],
        Callable[[str, str], None],
    ],
    Gym[
        WordleMetaConfig,
        WordleMutableMetaConfig,
        WordleConfig,
        WordleInfo,
        WordleGuess,
        WordleFeedback,
        WordleFinalResult,
    ],
] = make_input_config_reader_log_game_renderer(
    input_config_reader_cls=WordleInputConfigReader,
    config_generator_cls=WordleConfigGenerator,
    game_engine_cls=WordleGameEngine,
    log_game_renderer_cls=WordleLogGameRenderer,
)
