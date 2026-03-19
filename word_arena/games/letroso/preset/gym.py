from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..config.loader import LetrosoConfigLoader
from ..config.reader.input import LetrosoInputConfigReader
from ..game.engine import LetrosoGameEngine
from ..game.renderer.log import LetrosoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=LetrosoConfigLoader(
            meta_config=LetrosoMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=LetrosoInputConfigReader(input_func=input_func),
        ),
        engine_cls=LetrosoGameEngine,
        renderer=LetrosoLogGameRenderer(game_log_func=log_func),
    )
