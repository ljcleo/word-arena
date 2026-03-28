from importlib import import_module

from build_llm import build_llm
from common import log, make_cls_prefix

from word_arena.common.player.player import Player
from word_arena.players.agent.engine import AgentPlayerEngine
from word_arena.players.agent.prompter.base import BaseAgentPrompter
from word_arena.players.agent.renderer.log import AgentLogPlayerRenderer


def build_agent_player(*, game_key: str, llm_key: str) -> Player:
    prompter_cls: type[BaseAgentPrompter] = getattr(
        import_module(f"word_arena.games.{game_key}.players.agent.prompter"),
        f"{make_cls_prefix(key=game_key)}AgentPrompter",
    )

    return Player(
        engine=AgentPlayerEngine(
            prompter=prompter_cls(),
            model=build_llm(llm_key=llm_key),
            do_analyze=input("Analyze? (y/n): ")[0].lower() == "y",
        ),
        renderer=AgentLogPlayerRenderer(player_log_func=log),
    )
