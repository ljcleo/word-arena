from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from common import log
from pydantic import BaseModel

from word_arena.common.gym.gym import Gym

GAME_CONFIG_PATH: Path = Path("./config/games")


class GameConfig(BaseModel):
    meta_config: dict[str, Any]
    mutable_meta_config_pool: list[Any]


def build_gym(*, game_key: str) -> Gym:
    with (GAME_CONFIG_PATH / f"{game_key}.json").open("rb") as f:
        config: GameConfig = GameConfig.model_validate_json(f.read())

    prefix: str = "".join(part.capitalize() for part in game_key.split("_"))
    config_module: ModuleType = import_module(f"word_arena.games.{game_key}.config.common")
    meta_cls: type[BaseModel] = getattr(config_module, f"{prefix}MetaConfig")
    mutable_cls: type[BaseModel] | None = getattr(config_module, f"{prefix}MutableMetaConfig", None)

    return import_module(
        f"word_arena.games.{game_key}.preset.gym"
    ).input_config_reader_log_game_renderer(
        meta_cls.model_validate(config.meta_config),
        [
            config if mutable_cls is None else mutable_cls.model_validate(config)
            for config in config.mutable_meta_config_pool
        ],
        input,
        log,
    )
