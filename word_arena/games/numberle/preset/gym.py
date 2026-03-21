from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import NumberleMetaConfig, NumberleMutableMetaConfig
from ..config.generator import NumberleConfigGenerator
from ..config.reader.input import NumberleInputConfigReader
from ..game.engine import NumberleGameEngine
from ..game.renderer.log import NumberleLogGameRenderer


def numberle_input_config_reader_log_game_renderer(
    *,
    meta_config: NumberleMetaConfig,
    mutable_meta_config_pool: Sequence[NumberleMutableMetaConfig],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=NumberleInputConfigReader,
        config_generator_cls=NumberleConfigGenerator,
        game_engine_cls=NumberleGameEngine,
        log_game_renderer_cls=NumberleLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
