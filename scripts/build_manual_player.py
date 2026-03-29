from importlib import import_module
from types import ModuleType
from typing import Any

from common import GAME_CONFIG_PATH
from pydantic import BaseModel
from utils import make_cls_prefix, try_validate

from word_arena.common.player.player import Player
from word_arena.players.manual.engine import ManualPlayerEngine
from word_arena.players.manual.reader.input import BaseInputManualReader
from word_arena.players.manual.renderer.log import ManualLogPlayerRenderer


class ManualPlayerConfig(BaseModel):
    input_prompt: Any


def build_manual_player(*, game_key: str) -> Player:
    with (GAME_CONFIG_PATH / game_key / "players" / "manual.json").open("rb") as f:
        config: ManualPlayerConfig = ManualPlayerConfig.model_validate_json(f.read(), strict=True)

    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}.players.manual"
    reader_module: ModuleType = import_module(f"{module_parent}.reader.input")

    reader_cls: type[BaseInputManualReader] = getattr(
        reader_module, f"{cls_prefix}InputManualReader"
    )

    prompt_config_cls: type[BaseModel] | None = getattr(
        reader_module, f"{cls_prefix}InputPromptConfig", None
    )

    return Player(
        engine=ManualPlayerEngine(
            reader=reader_cls(
                input_func=input,
                prompt_config=try_validate(cls=prompt_config_cls, data=config.input_prompt),
            )
        ),
        renderer=ManualLogPlayerRenderer(),
    )
