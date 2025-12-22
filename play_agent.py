from collections.abc import Callable

from word_arena.common.gym.agent import BaseAgentGym


def build_contexto_agent_gym(seed: int) -> BaseAgentGym:
    from word_arena.games.contexto.generators.common import ContextoSetting
    from word_arena.games.contexto.gyms.agent import ContextoAgentGym

    return ContextoAgentGym(setting_pool=(ContextoSetting(max_guesses=50),), seed=seed)


def build_contexto_hint_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.generators.common import ContextoHintSetting
    from word_arena.games.contexto_hint.gyms.agent import ContextoHintAgentGym

    return ContextoHintAgentGym(
        setting_pool=(ContextoHintSetting(num_candidates=5),),
        seed=seed,
        games_dir=Path("./data/contexto_hint/games"),
    )


def build_wordle_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.wordle.generators.common import WordleSetting
    from word_arena.games.wordle.gyms.agent import WordleAgentGym

    return WordleAgentGym(
        setting_pool=(
            WordleSetting(num_targets=num_targets, max_guesses=num_targets + 5)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        word_list_file=Path("./data/wordle/words.txt"),
    )


def build_letroso_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.letroso.generators.common import LetrosoSetting
    from word_arena.games.letroso.gyms.agent import LetrosoAgentGym

    return LetrosoAgentGym(
        setting_pool=(LetrosoSetting(num_targets=1, max_letters=10, max_guesses=20),),
        seed=seed,
        word_list_file=Path("./data/letroso/words.txt"),
    )


def build_conexo_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.conexo.generators.common import ConexoSetting
    from word_arena.games.conexo.gyms.agent import ConexoAgentGym

    return ConexoAgentGym(
        setting_pool=(ConexoSetting(max_guesses=20),),
        seed=seed,
        games_dir=Path("./data/conexo/games"),
    )


AGENT_GYM_BUILDERS: dict[str, Callable[[int], BaseAgentGym]] = {
    "contexto": build_contexto_agent_gym,
    "contexto-hint": build_contexto_hint_agent_gym,
    "wordle": build_wordle_agent_gym,
    "letroso": build_letroso_agent_gym,
    "conexo": build_conexo_agent_gym,
}


def main():
    from time import time_ns

    from word_arena.common.player.agent.common import PromptMode
    from word_arena.llms.openai import OpenaiLLM

    games: list[str] = list(AGENT_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index + 1}. {game}")

    AGENT_GYM_BUILDERS[games[int(input("Game Index: ")) - 1]](time_ns()).play(
        OpenaiLLM(
            api_key="sk-PInpH3EcNkJjwzqvB1EbBdF09e9b4b12A81fF0C325D55d71",
            base_url="https://openkey.cloud/v1",
            model=input("LLM Model: "),
            max_tokens=32768,
            timeout=7200,
            use_dev_message=True,
            log_file="llm.log",
        ),
        (
            PromptMode.MULTI_TURN
            if input("Multi-turn? (y/n): ")[0].lower() == "y"
            else PromptMode.DIRECT
        )
        if input("Analyze? (y/n): ")[0].lower() == "y"
        else PromptMode.SIMPLE,
    )


if __name__ == "__main__":
    main()
