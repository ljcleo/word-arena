from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import ContextoMetaConfig
from ..config.generator import ContextoConfigGenerator
from ..config.reader.input import ContextoInputConfigReader
from ..game.engine import ContextoGameEngine
from ..game.renderer.log import ContextoLogGameRenderer


def contexto_input_config_reader_log_game_renderer(
    *,
    meta_config: ContextoMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=ContextoInputConfigReader,
        config_generator_cls=ContextoConfigGenerator,
        game_engine_cls=ContextoGameEngine,
        log_game_renderer_cls=ContextoLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
