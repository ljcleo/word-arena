from collections.abc import Callable, Sequence

from ..config.generator.base import BaseConfigGenerator
from ..config.reader.input import BaseInputConfigReader
from ..game.engine.base import BaseGameEngine
from ..game.renderer.log import BaseLogGameRenderer
from .gym import Gym


def make_input_config_reader_log_game_renderer[MT, UT, CT, IT, GT, FT, RT](
    *,
    input_config_reader_cls: type[BaseInputConfigReader[MT, CT]],
    config_generator_cls: type[BaseConfigGenerator[MT, UT, CT]],
    game_engine_cls: type[BaseGameEngine[CT, IT, GT, FT, RT]],
    log_game_renderer_cls: type[BaseLogGameRenderer[IT, GT, FT, RT]],
):
    def input_config_reader_log_game_renderer(
        meta_config: MT,
        mutable_meta_config_pool: Sequence[UT],
        input_func: Callable[[str], str],
        log_func: Callable[[str, str], None],
    ) -> Gym[MT, UT, CT, IT, GT, FT, RT]:
        return Gym(
            meta_config=meta_config,
            mutable_meta_config_pool=mutable_meta_config_pool,
            config_reader=input_config_reader_cls(input_func=input_func),
            config_generator=config_generator_cls(),
            game_engine_cls=game_engine_cls,
            game_renderer=log_game_renderer_cls(game_log_func=log_func),
        )

    return input_config_reader_log_game_renderer
