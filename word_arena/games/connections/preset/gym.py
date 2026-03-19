from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import ConnectionsMetaConfig
from ..config.loader import ConnectionsConfigLoader
from ..config.reader.input import ConnectionsInputConfigReader
from ..game.engine import ConnectionsGameEngine
from ..game.renderer.log import ConnectionsLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=ConnectionsConfigLoader(
            meta_config=ConnectionsMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ConnectionsInputConfigReader(input_func=input_func),
        ),
        engine_cls=ConnectionsGameEngine,
        renderer=ConnectionsLogGameRenderer(game_log_func=log_func),
    )
