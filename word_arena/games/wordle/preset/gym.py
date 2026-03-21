from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import WordleMetaConfig, WordleMutableMetaConfig
from ..config.generator import WordleConfigGenerator
from ..config.reader.input import WordleInputConfigReader
from ..game.engine import WordleGameEngine
from ..game.renderer.log import WordleLogGameRenderer


def wordle_input_config_reader_log_game_renderer(
    *,
    meta_config: WordleMetaConfig,
    mutable_meta_config_pool: Sequence[WordleMutableMetaConfig],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=WordleInputConfigReader,
        config_generator_cls=WordleConfigGenerator,
        game_engine_cls=WordleGameEngine,
        log_game_renderer_cls=WordleLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
