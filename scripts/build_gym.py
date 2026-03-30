from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from common import GAME_CONFIG_PATH, log
from pydantic import BaseModel
from utils import make_cls_prefix, try_validate

from word_arena.common.config.generator.base import BaseConfigGenerator
from word_arena.common.config.selector.input import BaseInputConfigSelector
from word_arena.common.game.engine.base import BaseGameEngine
from word_arena.common.game.renderer.log import LogGameRenderer
from word_arena.common.gym.gym import Gym


class GameConfig(BaseModel):
    meta_config: dict[str, Any]
    mutable_meta_config_pool: list[Any]


def build_gym(*, game_key: str) -> Gym:
    game_path: Path = GAME_CONFIG_PATH / game_key
    with (game_path / "game.json").open("rb") as f:
        config: GameConfig = GameConfig.model_validate_json(f.read(), strict=True)

    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}"

    config_module: ModuleType = import_module(f"{module_parent}.config.common")
    meta_config_cls: type[BaseModel] = getattr(config_module, f"{cls_prefix}MetaConfig")

    mutable_meta_config_cls: type[BaseModel] | None = getattr(
        config_module, f"{cls_prefix}MutableMetaConfig", None
    )

    config_selector_cls: type[BaseInputConfigSelector] = getattr(
        import_module(f"{module_parent}.config.selector.input"), f"{cls_prefix}InputConfigSelector"
    )

    config_generator_cls: type[BaseConfigGenerator] = getattr(
        import_module(f"{module_parent}.config.generator"), f"{cls_prefix}ConfigGenerator"
    )

    game_engine_cls: type[BaseGameEngine] = getattr(
        import_module(f"{module_parent}.game.engine"), f"{cls_prefix}GameEngine"
    )

    return Gym(
        meta_config=try_validate(cls=meta_config_cls, data=config.meta_config),
        mutable_meta_config_pool=[
            try_validate(cls=mutable_meta_config_cls, data=config)
            for config in config.mutable_meta_config_pool
        ],
        config_selector=config_selector_cls(input_func=input),
        config_generator=config_generator_cls(),
        game_engine_cls=game_engine_cls,
        game_renderer=LogGameRenderer(
            game_log_func=log, template_path=game_path / "templates" / "log_renderer"
        ),
    )
