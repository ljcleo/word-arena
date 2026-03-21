from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import RedactleMetaConfig
from ..config.generator import RedactleConfigGenerator
from ..config.reader.input import RedactleInputConfigReader
from ..game.engine import RedactleGameEngine
from ..game.renderer.log import RedactleLogGameRenderer


def redactle_input_config_reader_log_game_renderer(
    *,
    meta_config: RedactleMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=RedactleInputConfigReader,
        config_generator_cls=RedactleConfigGenerator,
        game_engine_cls=RedactleGameEngine,
        log_game_renderer_cls=RedactleLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
