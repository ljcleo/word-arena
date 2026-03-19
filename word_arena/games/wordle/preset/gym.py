from collections.abc import Callable, Iterable
from pathlib import Path

from ....common.gym.gym import Gym
from ..config.common import WordleMetaConfig, WordleMutableMetaConfig
from ..config.loader import WordleConfigLoader
from ..config.reader.input import WordleInputConfigReader
from ..game.engine import WordleGameEngine
from ..game.renderer.log import WordleLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[WordleMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> Gym:
    return Gym(
        config_loader=WordleConfigLoader(
            meta_config=WordleMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=WordleInputConfigReader(input_func=input_func),
        ),
        engine_cls=WordleGameEngine,
        renderer=WordleLogGameRenderer(game_log_func=log_func),
    )
