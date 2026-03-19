from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import StrandsMetaConfig
from ..game.config.loader import StrandsConfigLoader
from ..game.config.reader.input import StrandsInputConfigReader
from ..game.loader import StrandsGameLoader
from ..game.renderer.log import StrandsLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[StrandsConfigLoader, StrandsGameLoader]:
    return (
        StrandsConfigLoader(
            meta_config=StrandsMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=StrandsInputConfigReader(input_func=input_func),
        ),
        StrandsGameLoader(renderer=StrandsLogGameRenderer(game_log_func=log_func)),
    )
