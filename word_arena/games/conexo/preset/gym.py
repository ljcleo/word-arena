from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import ConexoMetaConfig
from ..config.loader import ConexoConfigLoader
from ..config.reader.input import ConexoInputConfigReader
from ..game.engine import ConexoGameEngine
from ..game.renderer.log import ConexoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=ConexoConfigLoader(
            meta_config=ConexoMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ConexoInputConfigReader(input_func=input_func),
        ),
        engine_cls=ConexoGameEngine,
        renderer=ConexoLogGameRenderer(game_log_func=log_func),
    )
