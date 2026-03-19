from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import TuringMetaConfig, TuringMutableMetaConfig
from ..config.loader import TuringConfigLoader
from ..config.reader.input import TuringInputConfigReader
from ..game.engine import TuringGameEngine
from ..game.renderer.log import TuringLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[TuringMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=TuringConfigLoader(
            meta_config=TuringMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=TuringInputConfigReader(input_func=input_func),
        ),
        engine_cls=TuringGameEngine,
        renderer=TuringLogGameRenderer(game_log_func=log_func),
    )
