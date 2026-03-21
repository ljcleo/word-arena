from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import StrandsMetaConfig
from ..config.generator import StrandsConfigGenerator
from ..config.reader.input import StrandsInputConfigReader
from ..game.engine import StrandsGameEngine
from ..game.renderer.log import StrandsLogGameRenderer


def strands_input_config_reader_log_game_renderer(
    *,
    meta_config: StrandsMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=StrandsInputConfigReader,
        config_generator_cls=StrandsConfigGenerator,
        game_engine_cls=StrandsGameEngine,
        log_game_renderer_cls=StrandsLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
