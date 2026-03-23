from importlib import import_module

from build_llm import build_llm
from common import log, make_cls_prefix

from word_arena.players.agent.engine.llm import BaseLLMAgentEngine
from word_arena.players.agent.player import AgentPlayer
from word_arena.players.agent.renderer.log import LogAgentRenderer


def build_player(*, game_key: str, llm_key: str) -> AgentPlayer:
    engine_cls: type[BaseLLMAgentEngine] = getattr(
        import_module(f"word_arena.games.{game_key}.players.agent.engine.llm"),
        f"{make_cls_prefix(key=game_key)}LLMAgentEngine",
    )

    return AgentPlayer(
        engine=engine_cls(
            model=build_llm(llm_key=llm_key), do_analyze=input("Analyze? (y/n): ")[0].lower() == "y"
        ),
        renderer=LogAgentRenderer(agent_log_func=log),
    )
