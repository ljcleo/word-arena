from collections.abc import Callable
from pathlib import Path

from common import build_gym, log

from word_arena.common.gym.gym import Gym
from word_arena.common.llm.base import BaseLLM
from word_arena.players.agent.engine.llm import BaseLLMAgentEngine
from word_arena.players.agent.player import AgentPlayer
from word_arena.players.agent.renderer.log import BaseLogAgentRenderer


def build_contexto_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.contexto.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_contexto_hint_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.contexto_hint.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_wordle_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.wordle.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_letroso_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.letroso.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_conexo_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.conexo.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_numberle_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.numberle.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_connections_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.connections.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_strands_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.strands.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


def build_turing_player_components(
    model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[BaseLLMAgentEngine, BaseLogAgentRenderer]:
    from word_arena.games.turing.preset.players.agent import llm_engine_log_renderer

    return llm_engine_log_renderer(model=model, do_analyze=do_analyze, log_func=log_func)


PLAYER_COMPONENT_BUILDERS: dict[
    str,
    Callable[
        [BaseLLM, bool, Callable[[str, str], None]],
        tuple[BaseLLMAgentEngine, BaseLogAgentRenderer],
    ],
] = {
    "contexto": build_contexto_player_components,
    "contexto-hint": build_contexto_hint_player_components,
    "wordle": build_wordle_player_components,
    "letroso": build_letroso_player_components,
    "conexo": build_conexo_player_components,
    "numberle": build_numberle_player_components,
    "connections": build_connections_player_components,
    "strands": build_strands_player_components,
    "turing": build_turing_player_components,
}


def build_player(*, game_key: str) -> AgentPlayer:
    from typing import Any, Literal

    from pydantic import BaseModel

    class LLMConfig(BaseModel):
        type: Literal["pseudo", "openai_chat", "openai_responses", "anthropic", "google"]
        config: dict[str, Any]

    with (Path("./config/llm") / f"{input('LLM config: ').lower()}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read())

    model: BaseLLM

    if config.type == "pseudo":
        from word_arena.llms.pseudo import PseudoLLM, PseudoLLMConfig

        model = PseudoLLM(config=PseudoLLMConfig.model_validate(config.config), llm_log_func=log)
    elif config.type == "openai_chat":
        from word_arena.llms.openai_chat import OpenaiChatLLM, OpenaiChatLLMConfig

        model = OpenaiChatLLM(config=OpenaiChatLLMConfig.model_validate(config.config))
    elif config.type == "openai_responses":
        from word_arena.llms.openai_responses import OpenaiResponsesLLM, OpenaiResponsesLLMConfig

        model = OpenaiResponsesLLM(config=OpenaiResponsesLLMConfig.model_validate(config.config))
    elif config.type == "anthropic":
        from word_arena.llms.anthropic import AnthropicLLM, AnthropicLLMConfig

        model = AnthropicLLM(
            config=AnthropicLLMConfig.model_validate(config.config), llm_log_func=log
        )
    elif config.type == "google":
        from word_arena.llms.google import GoogleLLM, GoogleLLMConfig

        model = GoogleLLM(config=GoogleLLMConfig.model_validate(config.config), llm_log_func=log)
    else:
        raise RuntimeError(config.type)

    player_engine: BaseLLMAgentEngine
    player_renderer: BaseLogAgentRenderer

    player_engine, player_renderer = PLAYER_COMPONENT_BUILDERS[game_key](
        model, input("Analyze? (y/n): ")[0].lower() == "y", log
    )

    return AgentPlayer(engine=player_engine, renderer=player_renderer)


def main() -> None:
    games: list[str] = list(PLAYER_COMPONENT_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    game_key: str = games[int(input("Game Index: "))]
    gym: Gym = build_gym(game_key=game_key)
    player: AgentPlayer = build_player(game_key=game_key)

    if input("Train? (y/n): ")[0].lower() == "y":
        from time import time_ns

        from word_arena.common.gym.common import TrainingConfig

        gym.train(
            player=player,
            training_config=TrainingConfig(
                num_train_loops=int(input("Number of Train Loops: ")),
                num_in_loop_trials=int(input("Number of In-Loop Trials: ")),
                seed=time_ns(),
            ),
        )

    gym.play(player=player)


if __name__ == "__main__":
    main()
