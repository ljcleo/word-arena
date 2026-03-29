from importlib import import_module
from types import ModuleType
from typing import Any

from build_llm import build_llm
from common import GAME_CONFIG_PATH, PLAYER_CONFIG_PATH, log
from pydantic import BaseModel
from utils import make_cls_prefix, try_validate

from word_arena.common.player.player import Player
from word_arena.players.agent.engine import AgentHintPromptConfig, AgentPlayerEngine
from word_arena.players.agent.prompter.base import BaseAgentPrompter
from word_arena.players.agent.renderer.log import AgentLogPlayerRenderer, AgentLogPromptConfig


class AgentPlayerGlobalConfig(BaseModel):
    hint_prompt: AgentHintPromptConfig
    log_prompt: AgentLogPromptConfig


class AgentPlayerLocalConfig(BaseModel):
    prompter_prompt: Any


def build_agent_player(*, game_key: str, llm_key: str) -> Player:
    with (PLAYER_CONFIG_PATH / "agent.json").open("rb") as f:
        global_config: AgentPlayerGlobalConfig = AgentPlayerGlobalConfig.model_validate_json(
            f.read(), strict=True
        )

    with (GAME_CONFIG_PATH / game_key / "players" / "agent.json").open("rb") as f:
        local_config: AgentPlayerLocalConfig = AgentPlayerLocalConfig.model_validate_json(
            f.read(), strict=True
        )

    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}.players.agent"
    prompter_module: ModuleType = import_module(f"{module_parent}.prompter")
    prompter_cls: type[BaseAgentPrompter] = getattr(prompter_module, f"{cls_prefix}AgentPrompter")

    prompt_config_cls: type[BaseModel] | None = getattr(
        prompter_module, f"{cls_prefix}AgentPrompterPromptConfig", None
    )

    return Player(
        engine=AgentPlayerEngine(
            model=build_llm(llm_key=llm_key),
            do_analyze=input("Analyze? (y/n): ")[0].lower() == "y",
            prompter=prompter_cls(
                prompt_config=try_validate(cls=prompt_config_cls, data=local_config.prompter_prompt)
            ),
            prompt_config=global_config.hint_prompt,
        ),
        renderer=AgentLogPlayerRenderer(
            player_log_func=log, prompt_config=global_config.log_prompt
        ),
    )
