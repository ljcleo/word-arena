from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import ConexoMetaConfig
from ..game.config.loader import ConexoConfigLoader
from ..game.config.reader.input import ConexoInputConfigReader
from ..game.loader import ConexoGameLoader
from ..game.renderer.log import ConexoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[ConexoConfigLoader, ConexoGameLoader]:
    return (
        ConexoConfigLoader(
            meta_config=ConexoMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ConexoInputConfigReader(input_func=input_func),
        ),
        ConexoGameLoader(renderer=ConexoLogGameRenderer(game_log_func=log_func)),
    )
