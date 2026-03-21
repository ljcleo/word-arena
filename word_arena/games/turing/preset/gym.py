from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import TuringMetaConfig, TuringMutableMetaConfig
from ..config.generator import TuringConfigGenerator
from ..config.reader.input import TuringInputConfigReader
from ..game.engine import TuringGameEngine
from ..game.renderer.log import TuringLogGameRenderer


def turing_input_config_reader_log_game_renderer(
    *,
    meta_config: TuringMetaConfig,
    mutable_meta_config_pool: Sequence[TuringMutableMetaConfig],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=TuringInputConfigReader,
        config_generator_cls=TuringConfigGenerator,
        game_engine_cls=TuringGameEngine,
        log_game_renderer_cls=TuringLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
