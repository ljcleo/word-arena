from collections.abc import Callable

from word_arena.common.gym.agent.gym import BaseAgentGym


def build_contexto_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from word_arena.games.contexto.generators.common import ContextoConfig, ContextoSetting
    from word_arena.games.contexto.gyms.agent import ContextoAgentGym

    def create_config() -> ContextoConfig:
        return ContextoConfig(
            game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
        )

    return ContextoAgentGym(
        setting_pool=(ContextoSetting(max_guesses=50),),
        seed=seed,
        create_config_func=create_config,
        log_func=log_func,
    )


def build_contexto_hint_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.generators.common import (
        ContextoHintConfig,
        ContextoHintSetting,
    )
    from word_arena.games.contexto_hint.gyms.agent import ContextoHintAgentGym

    def create_config() -> ContextoHintConfig:
        return ContextoHintConfig(
            game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
        )

    return ContextoHintAgentGym(
        setting_pool=(ContextoHintSetting(num_candidates=5),),
        seed=seed,
        games_dir=Path("./data/contexto_hint/games"),
        create_config_func=create_config,
        log_func=log_func,
    )


def build_wordle_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from word_arena.games.wordle.generators.common import WordleConfig, WordleSetting
    from word_arena.games.wordle.gyms.agent import WordleAgentGym

    with open("./data/wordle/words.txt", encoding="utf8") as f:
        word_list: list[str] = list(map(str.strip, f))

    def create_config() -> WordleConfig:
        return WordleConfig(
            word_list=word_list,
            target_ids=[
                int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
            ],
            max_guesses=int(input("Max Guesses: ")),
        )

    return WordleAgentGym(
        setting_pool=(
            WordleSetting(num_targets=num_targets, max_guesses=num_targets + 5)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        word_list=word_list,
        create_config_func=create_config,
        log_func=log_func,
    )


def build_letroso_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from word_arena.games.letroso.generators.common import LetrosoConfig, LetrosoSetting
    from word_arena.games.letroso.gyms.agent import LetrosoAgentGym

    with open("./data/letroso/words.txt", encoding="utf8") as f:
        word_list: list[str] = list(map(str.strip, f))

    def create_config() -> LetrosoConfig:
        return LetrosoConfig(
            word_list=word_list,
            target_ids=[
                int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
            ],
            max_letters=int(input("Max Input Letters: ")),
            max_guesses=int(input("Max Guesses: ")),
        )

    return LetrosoAgentGym(
        setting_pool=(LetrosoSetting(num_targets=1, max_letters=10, max_guesses=20),),
        seed=seed,
        word_list=word_list,
        create_config_func=create_config,
        log_func=log_func,
    )


def build_conexo_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.conexo.generators.common import ConexoConfig, ConexoSetting
    from word_arena.games.conexo.gyms.agent import ConexoAgentGym

    def create_config() -> ConexoConfig:
        return ConexoConfig(
            game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
        )

    return ConexoAgentGym(
        setting_pool=(ConexoSetting(max_guesses=20),),
        seed=seed,
        games_dir=Path("./data/conexo/games"),
        create_config_func=create_config,
        log_func=log_func,
    )


AGENT_GYM_BUILDERS: dict[str, Callable[[int, Callable[[str], None]], BaseAgentGym]] = {
    "contexto": build_contexto_agent_gym,
    "contexto-hint": build_contexto_hint_agent_gym,
    "wordle": build_wordle_agent_gym,
    "letroso": build_letroso_agent_gym,
    "conexo": build_conexo_agent_gym,
}


def main() -> None:
    from time import time_ns

    from word_arena.common.gym.agent.common import TrainingConfig
    from word_arena.common.llm.base import BaseLLM
    from word_arena.llms.openai import OpenaiConfig, OpenaiLLM
    from word_arena.llms.pseudo import PseudoLLM

    model: BaseLLM

    if input("Use LLM? (y/n): ")[0].lower() == "y":
        with open("./config/openai.json", "rb") as f:
            model = OpenaiLLM(config=OpenaiConfig.model_validate_json(f.read()))
    else:
        model = PseudoLLM()

    do_analyze: bool = input("Analyze? (y/n): ")[0].lower() == "y"

    games: list[str] = list(AGENT_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    AGENT_GYM_BUILDERS[games[int(input("Game Index: "))]](time_ns(), print).play(
        model,
        do_analyze,
        TrainingConfig(
            num_train_loops=int(input("Number of Train Loops: ")),
            num_in_loop_trials=int(input("Number of In-Loop Trials: ")),
        )
        if input("Train? (y/n): ")[0].lower() == "y"
        else None,
        print,
        print,
    )


if __name__ == "__main__":
    main()
