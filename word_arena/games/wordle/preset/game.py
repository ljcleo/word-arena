from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import WordleMetaConfig, WordleMutableMetaConfig
from ..game.config.loader import WordleConfigLoader
from ..game.config.reader.input import WordleInputConfigReader
from ..game.loader import WordleGameLoader
from ..game.renderer.log import WordleLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[WordleMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[WordleConfigLoader, WordleGameLoader]:
    return (
        WordleConfigLoader(
            meta_config=WordleMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=WordleInputConfigReader(input_func=input_func),
        ),
        WordleGameLoader(renderer=WordleLogGameRenderer(game_log_func=log_func)),
    )
