from importlib import import_module

from build_llm import build_llm
from common import log

from word_arena.players.agent.player import AgentPlayer


def build_player(*, game_key: str, llm_key: str) -> AgentPlayer:
    return import_module(
        f"word_arena.games.{game_key}.preset.players.agent"
    ).llm_engine_log_renderer(
        build_llm(llm_key=llm_key), input("Analyze? (y/n): ")[0].lower() == "y", log
    )
