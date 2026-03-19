from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import ContextoHintMetaConfig
from ..game.config.loader import ContextoHintConfigLoader
from ..game.config.reader.input import ContextoHintInputConfigReader
from ..game.loader import ContextoHintGameLoader
from ..game.renderer.log import ContextoHintLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[ContextoHintConfigLoader, ContextoHintGameLoader]:
    return (
        ContextoHintConfigLoader(
            meta_config=ContextoHintMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ContextoHintInputConfigReader(input_func=input_func),
        ),
        ContextoHintGameLoader(renderer=ContextoHintLogGameRenderer(game_log_func=log_func)),
    )
