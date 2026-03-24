from importlib import import_module
from types import ModuleType
from typing import Any

from common import GAME_CONFIG_PATH, make_cls_prefix
from pydantic import BaseModel

from word_arena.players.manual.player import ManualPlayer
from word_arena.players.manual.reader.input import BaseInputManualReader


class ManualPlayerConfig(BaseModel):
    input_prompt: Any


def build_player(*, game_key: str) -> ManualPlayer:
    cls_prefix: str = make_cls_prefix(key=game_key)
    with (GAME_CONFIG_PATH / game_key / "players" / "manual.json").open("rb") as f:
        config: ManualPlayerConfig = ManualPlayerConfig.model_validate_json(f.read())

    reader_module: ModuleType = import_module(
        f"word_arena.games.{game_key}.players.manual.reader.input"
    )

    reader_cls: type[BaseInputManualReader] = getattr(
        reader_module, f"{cls_prefix}InputManualReader"
    )

    prompt_config_cls: type[BaseModel] | None = getattr(
        reader_module, f"{cls_prefix}InputPromptConfig", None
    )

    return ManualPlayer(
        reader=reader_cls(
            input_func=input,
            prompt_config=config.input_prompt
            if prompt_config_cls is None
            else prompt_config_cls.model_validate(config.input_prompt),
        )
    )
