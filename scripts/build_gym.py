from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from common import GAME_CONFIG_PATH, log, make_cls_prefix
from pydantic import BaseModel

from word_arena.common.config.generator.base import BaseConfigGenerator
from word_arena.common.config.reader.input import BaseInputConfigReader
from word_arena.common.game.engine.base import BaseGameEngine
from word_arena.common.game.renderer.log import BaseLogGameRenderer
from word_arena.common.gym.gym import Gym


class GameConfig(BaseModel):
    meta_config: dict[str, Any]
    mutable_meta_config_pool: list[Any]


class RendererConfig(BaseModel):
    log_prompt: Any


def build_gym(*, game_key: str) -> Gym:
    game_config_path: Path = GAME_CONFIG_PATH / game_key
    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}"

    with (game_config_path / "meta_config.json").open("rb") as f:
        game_config: GameConfig = GameConfig.model_validate_json(f.read())
    with (game_config_path / "renderer.json").open("rb") as f:
        renderer_config: RendererConfig = RendererConfig.model_validate_json(f.read())

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

    game_renderer_module: ModuleType = import_module(f"{module_parent}.game.renderer.log")

    game_renderer_cls: type[BaseLogGameRenderer] = getattr(
        game_renderer_module, f"{cls_prefix}LogGameRenderer"
    )

    prompt_config_cls: type[BaseModel] | None = getattr(
        game_renderer_module, f"{cls_prefix}LogPromptConfig", None
    )

    return Gym(
        meta_config=meta_config_cls.model_validate(game_config.meta_config),
        mutable_meta_config_pool=[
            config
            if mutable_meta_config_cls is None
            else mutable_meta_config_cls.model_validate(config)
            for config in game_config.mutable_meta_config_pool
        ],
        config_reader=config_reader_cls(input_func=input),
        config_generator=config_generator_cls(),
        game_engine_cls=game_engine_cls,
        game_renderer=game_renderer_cls(
            game_log_func=log,
            prompt_config=(
                renderer_config.log_prompt
                if prompt_config_cls is None
                else prompt_config_cls.model_validate(renderer_config.log_prompt)
            ),
        ),
    )
