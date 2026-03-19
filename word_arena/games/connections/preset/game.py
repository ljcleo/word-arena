from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import ConnectionsMetaConfig
from ..game.config.loader import ConnectionsConfigLoader
from ..game.config.reader.input import ConnectionsInputConfigReader
from ..game.loader import ConnectionsGameLoader
from ..game.renderer.log import ConnectionsLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[ConnectionsConfigLoader, ConnectionsGameLoader]:
    return (
        ConnectionsConfigLoader(
            meta_config=ConnectionsMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ConnectionsInputConfigReader(input_func=input_func),
        ),
        ConnectionsGameLoader(renderer=ConnectionsLogGameRenderer(game_log_func=log_func)),
    )
