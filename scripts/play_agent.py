from collections.abc import Callable
from typing import Any

from build_agent_player import build_player
from build_gym import GYM_BUILDERS, build_gym
from common import log

from word_arena.common.gym.gym import Gym
from word_arena.common.llm.base import BaseLLM
from word_arena.players.agent.player import AgentPlayer


def build_pseudo_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.pseudo import PseudoLLM, PseudoLLMConfig

    return PseudoLLM(config=PseudoLLMConfig.model_validate(config), llm_log_func=log)


def build_openai_chat_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.openai_chat import OpenaiChatLLM, OpenaiChatLLMConfig

    return OpenaiChatLLM(config=OpenaiChatLLMConfig.model_validate(config))


def build_openai_responses_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.openai_responses import OpenaiResponsesLLM, OpenaiResponsesLLMConfig

    return OpenaiResponsesLLM(config=OpenaiResponsesLLMConfig.model_validate(config))


def build_anthropic_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.anthropic import AnthropicLLM, AnthropicLLMConfig

    return AnthropicLLM(config=AnthropicLLMConfig.model_validate(config), llm_log_func=log)


def build_google_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.google import GoogleLLM, GoogleLLMConfig

    return GoogleLLM(config=GoogleLLMConfig.model_validate(config), llm_log_func=log)


LLM_BUILDERS: dict[str, Callable[[dict[str, Any]], BaseLLM]] = {
    "pseudo": build_pseudo_llm,
    "openai-chat": build_openai_chat_llm,
    "openai-responses": build_openai_responses_llm,
    "anthropic": build_anthropic_llm,
    "google": build_google_llm,
}


def build_llm(*, llm_key: str, config: dict[str, Any]) -> BaseLLM:
    return LLM_BUILDERS[llm_key](config)


def main() -> None:
    games: list[str] = list(GYM_BUILDERS.keys())
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
