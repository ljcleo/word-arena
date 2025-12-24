from collections.abc import Callable

from word_arena.common.gym.agent.gym import BaseAgentGym


def build_contexto_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from word_arena.games.contexto.generators.common import ContextoConfig
    from word_arena.games.contexto.gyms.agent import ContextoAgentGym

    return ContextoAgentGym(
        mutable_meta_config_pool=(50,),
        seed=seed,
        log_func=log_func,
        config_creator=lambda: ContextoConfig(
            max_guesses=int(input("Max Guesses: ")), game_id=int(input("Game ID: "))
        ),
    )


def build_contexto_hint_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.generators.common import ContextoHintConfig
    from word_arena.games.contexto_hint.gyms.agent import ContextoHintAgentGym

    return ContextoHintAgentGym(
        mutable_meta_config_pool=(5,),
        seed=seed,
        log_func=log_func,
        data_file=Path("./data/contexto_hint/games.db"),
        config_creator=lambda: ContextoHintConfig(
            num_candidates=int(input("Number of Candidates: ")), game_id=int(input("Game ID: "))
        ),
    )


def build_wordle_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.wordle.generators.common import WordleConfig, WordleMutableMetaConfig
    from word_arena.games.wordle.gyms.agent import WordleAgentGym

    return WordleAgentGym(
        mutable_meta_config_pool=(
            WordleMutableMetaConfig(max_guesses=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        log_func=log_func,
        data_file=Path("./data/wordle/games.db"),
        config_creator=lambda: WordleConfig(
            max_guesses=int(input("Max Guesses: ")),
            game_ids=[int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))],
        ),
    )


def build_letroso_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.letroso.generators.common import LetrosoConfig, LetrosoMutableMetaConfig
    from word_arena.games.letroso.gyms.agent import LetrosoAgentGym

    return LetrosoAgentGym(
        mutable_meta_config_pool=(
            LetrosoMutableMetaConfig(max_letters=10, max_guesses=20, num_targets=1),
        ),
        seed=seed,
        log_func=log_func,
        data_file=Path("./data/letroso/games.db"),
        config_creator=lambda: LetrosoConfig(
            max_letters=int(input("Max Input Letters: ")),
            max_guesses=int(input("Max Guesses: ")),
            game_ids=[int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))],
        ),
    )


def build_conexo_agent_gym(seed: int, log_func: Callable[[str], None]) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.conexo.generators.common import ConexoConfig
    from word_arena.games.conexo.gyms.agent import ConexoAgentGym

    return ConexoAgentGym(
        mutable_meta_config_pool=(20,),
        seed=seed,
        log_func=log_func,
        data_file=Path("./data/conexo/games.db"),
        config_creator=lambda: ConexoConfig(
            max_guesses=int(input("Max Guesses: ")), game_id=int(input("Game ID: "))
        ),
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
