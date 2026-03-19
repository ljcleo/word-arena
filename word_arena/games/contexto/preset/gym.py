from collections.abc import Callable, Iterable

from ....common.gym.gym import Gym
from ..config.common import ContextoMetaConfig
from ..config.loader import ContextoConfigLoader
from ..config.reader.input import ContextoInputConfigReader
from ..game.engine import ContextoGameEngine
from ..game.renderer.log import ContextoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    base_url: str,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=ContextoConfigLoader(
            meta_config=ContextoMetaConfig(base_url=base_url),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ContextoInputConfigReader(input_func=input_func),
        ),
        engine_cls=ContextoGameEngine,
        renderer=ContextoLogGameRenderer(game_log_func=log_func),
    )
