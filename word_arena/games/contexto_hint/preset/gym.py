from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import ContextoHintMetaConfig
from ..config.loader import ContextoHintConfigLoader
from ..config.reader.input import ContextoHintInputConfigReader
from ..game.engine import ContextoHintGameEngine
from ..game.renderer.log import ContextoHintLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=ContextoHintConfigLoader(
            meta_config=ContextoHintMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ContextoHintInputConfigReader(input_func=input_func),
        ),
        engine_cls=ContextoHintGameEngine,
        renderer=ContextoHintLogGameRenderer(game_log_func=log_func),
    )
