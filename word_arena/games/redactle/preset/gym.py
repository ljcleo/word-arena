from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import RedactleMetaConfig
from ..config.loader import RedactleConfigLoader
from ..config.reader.input import RedactleInputConfigReader
from ..game.engine import RedactleGameEngine
from ..game.renderer.log import RedactleLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=RedactleConfigLoader(
            meta_config=RedactleMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=RedactleInputConfigReader(input_func=input_func),
        ),
        engine_cls=RedactleGameEngine,
        renderer=RedactleLogGameRenderer(game_log_func=log_func),
    )
