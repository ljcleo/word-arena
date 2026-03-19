from collections.abc import Callable, Iterable

from ..game.config.loader import ContextoConfigLoader
from ..game.config.reader.input import ContextoInputConfigReader
from ..game.loader import ContextoGameLoader
from ..game.renderer.log import ContextoLogGameRenderer


def input_config_reader_log_renderer(
    *,
    mutable_meta_config_pool: Iterable[int] | None,
    input_func: Callable[[str], str],
    log_func: Callable[[str, str], None],
) -> tuple[ContextoConfigLoader, ContextoGameLoader]:
    return (
        ContextoConfigLoader(
            meta_config=None,
            mutable_meta_config_pool=mutable_meta_config_pool,
            reader=ContextoInputConfigReader(input_func=input_func),
        ),
        ContextoGameLoader(renderer=ContextoLogGameRenderer(game_log_func=log_func)),
    )
