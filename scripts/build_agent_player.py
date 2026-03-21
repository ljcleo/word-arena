from importlib import import_module
from pathlib import Path
from typing import Any

from build_llm import build_llm
from common import log
from pydantic import BaseModel

from word_arena.players.agent.player import AgentPlayer


def build_player(*, game_key: str, llm_key: str) -> AgentPlayer:
    class LLMConfig(BaseModel):
        type: str
        config: dict[str, Any]

    with (Path("./config/llm") / f"{llm_key}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read())

    return import_module(
        f"word_arena.games.{game_key}.preset.players.agent"
    ).llm_engine_log_renderer(
        build_llm(llm_key=config.type, config=config.config),
        input("Analyze? (y/n): ")[0].lower() == "y",
        log,
    )
