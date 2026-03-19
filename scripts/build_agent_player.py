from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from build_llm import build_llm
from common import log

from word_arena.common.llm.base import BaseLLM
from word_arena.players.agent.player import AgentPlayer


def build_contexto_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.contexto.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_contexto_hint_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.contexto_hint.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_wordle_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.wordle.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_letroso_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.letroso.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_conexo_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.conexo.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_numberle_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.numberle.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_connections_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.connections.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_strands_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.strands.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_turing_player(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    from word_arena.games.turing.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


PLAYER_BUILDERS: dict[str, Callable[[BaseLLM, bool, Callable[[str, str], None]], AgentPlayer]] = {
    "contexto": build_contexto_player,
    "contexto-hint": build_contexto_hint_player,
    "wordle": build_wordle_player,
    "letroso": build_letroso_player,
    "conexo": build_conexo_player,
    "numberle": build_numberle_player,
    "connections": build_connections_player,
    "strands": build_strands_player,
    "turing": build_turing_player,
}


def build_player(*, game_key: str) -> AgentPlayer:
    from pydantic import BaseModel

    class LLMConfig(BaseModel):
        type: Literal["pseudo", "openai-chat", "openai-responses", "anthropic", "google"]
        config: dict[str, Any]

    llm_config_dir: Path = Path("./config/llm")
    llm_names: list[str] = sorted(p.stem for p in llm_config_dir.glob("*.json"))

    for index, name in enumerate(llm_names):
        print(f"{index}. {name}")

    with (Path("./config/llm") / f"{llm_names[int(input('LLM Index: '))]}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read())

    return PLAYER_BUILDERS[game_key](
        build_llm(llm_key=config.type, config=config.config),
        input("Analyze? (y/n): ")[0].lower() == "y",
        log,
    )
