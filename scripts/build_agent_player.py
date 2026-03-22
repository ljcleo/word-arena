from importlib import import_module

from build_llm import build_llm
from common import log, make_cls_prefix

from word_arena.players.agent.engine.llm import BaseLLMAgentEngine
from word_arena.players.agent.player import AgentPlayer
from word_arena.players.agent.renderer.log import BaseLogAgentRenderer


def build_player(*, game_key: str, llm_key: str) -> AgentPlayer:
    cls_prefix: str = make_cls_prefix(key=game_key)
    module_parent: str = f"word_arena.games.{game_key}.players.agent"

    engine_cls: type[BaseLLMAgentEngine] = getattr(
        import_module(f"{module_parent}.engine.llm"), f"{cls_prefix}LLMAgentEngine"
    )

    renderer_cls: type[BaseLogAgentRenderer] = getattr(
        import_module(f"{module_parent}.renderer.log"), f"{cls_prefix}LogAgentRenderer"
    )

    return AgentPlayer(
        engine=engine_cls(
            model=build_llm(llm_key=llm_key), do_analyze=input("Analyze? (y/n): ")[0].lower() == "y"
        ),
        renderer=renderer_cls(agent_log_func=log),
    )
