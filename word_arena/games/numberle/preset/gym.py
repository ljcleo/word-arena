from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import NumberleMetaConfig, NumberleMutableMetaConfig
from ..config.loader import NumberleConfigLoader
from ..config.reader.input import NumberleInputConfigReader
from ..game.engine import NumberleGameEngine
from ..game.renderer.log import NumberleLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[NumberleMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=NumberleConfigLoader(
            meta_config=NumberleMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=NumberleInputConfigReader(input_func=input_func),
        ),
        engine_cls=NumberleGameEngine,
        renderer=NumberleLogGameRenderer(game_log_func=log_func),
    )
