from collections.abc import Callable, Iterable
from pathlib import Path

from ..game.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
from ..game.config.loader import LetrosoConfigLoader
from ..game.config.reader.input import LetrosoInputConfigReader
from ..game.loader import LetrosoGameLoader
from ..game.renderer.log import LetrosoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    data_file: Path,
    mutable_meta_config_pool: Iterable[LetrosoMutableMetaConfig] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[LetrosoConfigLoader, LetrosoGameLoader]:
    return (
        LetrosoConfigLoader(
            meta_config=LetrosoMetaConfig(data_file=data_file),
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=LetrosoInputConfigReader(input_func=input_func),
        ),
        LetrosoGameLoader(renderer=LetrosoLogGameRenderer(game_log_func=log_func)),
    )
