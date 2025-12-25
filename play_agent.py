from collections.abc import Callable
from pathlib import Path

from word_arena.common.gym.agent.gym import BaseAgentGym


def build_contexto_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.contexto.gyms.agent import ContextoExampleAgentGym

    return ContextoExampleAgentGym(
        mutable_meta_config_pool=(50,), seed=seed, log_func=log_func, input_func=input_func
    )


def build_contexto_hint_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.contexto_hint.gyms.agent import ContextoHintExampleAgentGym

    return ContextoHintExampleAgentGym(
        data_file=Path("./data/contexto_hint/games.db"),
        mutable_meta_config_pool=(5,),
        seed=seed,
        log_func=log_func,
        input_func=input_func,
    )


def build_wordle_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.wordle.generators.common import WordleMutableMetaConfig
    from word_arena.games.wordle.gyms.agent import WordleExampleAgentGym

    return WordleExampleAgentGym(
        data_file=Path("./data/wordle/games.db"),
        mutable_meta_config_pool=(
            WordleMutableMetaConfig(max_guesses=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        log_func=log_func,
        input_func=input_func,
    )


def build_letroso_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.letroso.generators.common import LetrosoMutableMetaConfig
    from word_arena.games.letroso.gyms.agent import LetrosoExampleAgentGym

    return LetrosoExampleAgentGym(
        data_file=Path("./data/letroso/games.db"),
        mutable_meta_config_pool=(
            LetrosoMutableMetaConfig(max_letters=10, max_guesses=20, num_targets=1),
        ),
        seed=seed,
        log_func=log_func,
        input_func=input_func,
    )


def build_conexo_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.conexo.gyms.agent import ConexoExampleAgentGym

    return ConexoExampleAgentGym(
        data_file=Path("./data/conexo/games.db"),
        mutable_meta_config_pool=(20,),
        seed=seed,
        log_func=log_func,
        input_func=input_func,
    )


def build_numberle_agent_gym(
    seed: int, input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseAgentGym:
    from word_arena.games.numberle.generators.common import NumberleMutableMetaConfig
    from word_arena.games.numberle.gyms.agent import NumberleExampleAgentGym

    return NumberleExampleAgentGym(
        data_file=Path("./data/numberle/games.db"),
        mutable_meta_config_pool=(
            NumberleMutableMetaConfig(
                eq_length=eq_length, max_guesses=num_targets + 5, num_targets=num_targets
            )
            for eq_length in range(5, 13)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        log_func=log_func,
        input_func=input_func,
    )


AGENT_GYM_BUILDERS: dict[
    str, Callable[[int, Callable[[str], str], Callable[[str], None]], BaseAgentGym]
] = {
    "contexto": build_contexto_agent_gym,
    "contexto-hint": build_contexto_hint_agent_gym,
    "wordle": build_wordle_agent_gym,
    "letroso": build_letroso_agent_gym,
    "conexo": build_conexo_agent_gym,
    "numberle": build_numberle_agent_gym,
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

    AGENT_GYM_BUILDERS[games[int(input("Game Index: "))]](time_ns(), input, print).play(
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
