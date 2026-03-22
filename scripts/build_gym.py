from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from common import log, make_cls_prefix
from pydantic import BaseModel

from word_arena.common.config.generator.base import BaseConfigGenerator
from word_arena.common.config.reader.input import BaseInputConfigReader
from word_arena.common.game.engine.base import BaseGameEngine
from word_arena.common.game.renderer.log import BaseLogGameRenderer
from word_arena.common.gym.gym import Gym

GAME_CONFIG_PATH: Path = Path("./config/games")


class GameConfig(BaseModel):
    meta_config: dict[str, Any]
    mutable_meta_config_pool: list[Any]


def build_gym(*, game_key: str) -> Gym:
    with (GAME_CONFIG_PATH / f"{game_key}.json").open("rb") as f:
        config: GameConfig = GameConfig.model_validate_json(f.read())

    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}"
    config_module: ModuleType = import_module(f"{module_parent}.config.common")
    meta_config_cls: type[BaseModel] = getattr(config_module, f"{cls_prefix}MetaConfig")

    mutable_meta_config_cls: type[BaseModel] | None = getattr(
        config_module, f"{cls_prefix}MutableMetaConfig", None
    )

    config_reader_cls: type[BaseInputConfigReader] = getattr(
        import_module(f"{module_parent}.config.reader.input"), f"{cls_prefix}InputConfigReader"
    )

    config_generator_cls: type[BaseConfigGenerator] = getattr(
        import_module(f"{module_parent}.config.generator"), f"{cls_prefix}ConfigGenerator"
    )

    game_engine_cls: type[BaseGameEngine] = getattr(
        import_module(f"{module_parent}.game.engine"), f"{cls_prefix}GameEngine"
    )

    game_renderer_cls: type[BaseLogGameRenderer] = getattr(
        import_module(f"{module_parent}.game.renderer.log"), f"{cls_prefix}LogGameRenderer"
    )

    return Gym(
        meta_config=meta_config_cls.model_validate(config.meta_config),
        mutable_meta_config_pool=[
            config
            if mutable_meta_config_cls is None
            else mutable_meta_config_cls.model_validate(config)
            for config in config.mutable_meta_config_pool
        ],
        config_reader=config_reader_cls(input_func=input),
        config_generator=config_generator_cls(),
        game_engine_cls=game_engine_cls,
        game_renderer=game_renderer_cls(game_log_func=log),
    )
