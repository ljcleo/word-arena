from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import ContextoHintMetaConfig
from ..config.generator import ContextoHintConfigGenerator
from ..config.reader.input import ContextoHintInputConfigReader
from ..game.engine import ContextoHintGameEngine
from ..game.renderer.log import ContextoHintLogGameRenderer


def contexto_hint_input_config_reader_log_game_renderer(
    *,
    meta_config: ContextoHintMetaConfig,
    mutable_meta_config_pool: Sequence[int],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=ContextoHintInputConfigReader,
        config_generator_cls=ContextoHintConfigGenerator,
        game_engine_cls=ContextoHintGameEngine,
        log_game_renderer_cls=ContextoHintLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
