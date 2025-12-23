from collections.abc import Callable

from word_arena.common.gym.manual import BaseManualGym


def build_contexto_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from word_arena.games.contexto.generators.common import ContextoConfig
    from word_arena.games.contexto.gyms.manual import ContextoManualGym

    def create_config() -> ContextoConfig:
        return ContextoConfig(
            game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
        )

    return ContextoManualGym(create_config_func=create_config, log_func=log_func)


def build_contexto_hint_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.generators.common import ContextoHintConfig
    from word_arena.games.contexto_hint.gyms.manual import ContextoHintManualGym

    def create_config() -> ContextoHintConfig:
        return ContextoHintConfig(
            game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
        )

    return ContextoHintManualGym(
        games_dir=Path("./data/contexto_hint/games"),
        create_config_func=create_config,
        log_func=log_func,
    )


def build_wordle_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from word_arena.games.wordle.generators.common import WordleConfig
    from word_arena.games.wordle.gyms.manual import WordleManualGym

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

    return WordleManualGym(create_config_func=create_config, log_func=log_func)


def build_letroso_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from word_arena.games.letroso.generators.common import LetrosoConfig
    from word_arena.games.letroso.gyms.manual import LetrosoManualGym

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

    return LetrosoManualGym(create_config_func=create_config, log_func=log_func)


def build_conexo_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.conexo.generators.common import ConexoConfig
    from word_arena.games.conexo.gyms.manual import ConexoManualGym

    def create_config() -> ConexoConfig:
        return ConexoConfig(
            game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
        )

    return ConexoManualGym(
        games_dir=Path("./data/conexo/games"), create_config_func=create_config, log_func=log_func
    )


MANUAL_GYM_BUILDERS: dict[str, Callable[[Callable[[str], None]], BaseManualGym]] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
    "letroso": build_letroso_manual_gym,
    "conexo": build_conexo_manual_gym,
}


def main() -> None:
    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: "))]](print).play(input, print)


if __name__ == "__main__":
    main()
