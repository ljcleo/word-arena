from collections.abc import Callable, Sequence

from ....common.gym.gym import Gym
from ....common.gym.preset import input_config_reader_log_game_renderer
from ..config.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..config.generator import LetrosoConfigGenerator
from ..config.reader.input import LetrosoInputConfigReader
from ..game.engine import LetrosoGameEngine
from ..game.renderer.log import LetrosoLogGameRenderer


def letroso_input_config_reader_log_game_renderer(
    *,
    meta_config: LetrosoMetaConfig,
    mutable_meta_config_pool: Sequence[LetrosoMutableMetaConfig],
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return input_config_reader_log_game_renderer(
        meta_config=meta_config,
        mutable_meta_config_pool=mutable_meta_config_pool,
        input_config_reader_cls=LetrosoInputConfigReader,
        config_generator_cls=LetrosoConfigGenerator,
        game_engine_cls=LetrosoGameEngine,
        log_game_renderer_cls=LetrosoLogGameRenderer,
        input_func=input_func,
        log_func=log_func,
    )
