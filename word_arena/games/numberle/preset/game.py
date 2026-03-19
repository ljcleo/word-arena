from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import NumberleMetaConfig, NumberleMutableMetaConfig
from ..game.config.loader import NumberleConfigLoader
from ..game.config.reader.input import NumberleInputConfigReader
from ..game.loader import NumberleGameLoader
from ..game.renderer.log import NumberleLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[NumberleMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[NumberleConfigLoader, NumberleGameLoader]:
    return (
        NumberleConfigLoader(
            meta_config=NumberleMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=NumberleInputConfigReader(input_func=input_func),
        ),
        NumberleGameLoader(renderer=NumberleLogGameRenderer(game_log_func=log_func)),
    )
