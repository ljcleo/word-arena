from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import ConnectionsMetaConfig
from ..config.generator import ConnectionsConfigGenerator
from ..config.reader.input import ConnectionsInputConfigReader
from ..game.engine import ConnectionsGameEngine
from ..game.renderer.log import ConnectionsLogGameRenderer


def connections_input_config_reader_log_game_renderer(
    *,
    meta_config: ConnectionsMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=ConnectionsInputConfigReader,
        config_generator_cls=ConnectionsConfigGenerator,
        game_engine_cls=ConnectionsGameEngine,
        log_game_renderer_cls=ConnectionsLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
