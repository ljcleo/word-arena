from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import ConexoMetaConfig
from ..config.generator import ConexoConfigGenerator
from ..config.reader.input import ConexoInputConfigReader
from ..game.engine import ConexoGameEngine
from ..game.renderer.log import ConexoLogGameRenderer


def conexo_input_config_reader_log_game_renderer(
    *,
    meta_config: ConexoMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=ConexoInputConfigReader,
        config_generator_cls=ConexoConfigGenerator,
        game_engine_cls=ConexoGameEngine,
        log_game_renderer_cls=ConexoLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
