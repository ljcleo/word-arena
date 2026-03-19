from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import TuringMetaConfig, TuringMutableMetaConfig
from ..game.config.loader import TuringConfigLoader
from ..game.config.reader.input import TuringInputConfigReader
from ..game.loader import TuringGameLoader
from ..game.renderer.log import TuringLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[TuringMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[TuringConfigLoader, TuringGameLoader]:
    return (
        TuringConfigLoader(
            meta_config=TuringMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=TuringInputConfigReader(input_func=input_func),
        ),
        TuringGameLoader(renderer=TuringLogGameRenderer(game_log_func=log_func)),
    )
