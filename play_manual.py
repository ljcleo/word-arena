from collections.abc import Callable

from word_arena.common.gym.manual import BaseManualGym


def build_contexto_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from word_arena.games.contexto.generators.common import ContextoConfig
    from word_arena.games.contexto.gyms.manual import ContextoManualGym

    return ContextoManualGym(
        log_func=log_func,
        config_creator=lambda: ContextoConfig(
            max_guesses=int(input("Max Guesses: ")), game_id=int(input("Game ID: "))
        ),
    )


def build_contexto_hint_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.generators.common import ContextoHintConfig
    from word_arena.games.contexto_hint.gyms.manual import ContextoHintManualGym

    return ContextoHintManualGym(
        log_func=log_func,
        data_file=Path("./data/contexto_hint/games.db"),
        config_creator=lambda: ContextoHintConfig(
            num_candidates=int(input("Number of Candidates: ")), game_id=int(input("Game ID: "))
        ),
    )


def build_wordle_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.wordle.generators.common import WordleConfig
    from word_arena.games.wordle.gyms.manual import WordleManualGym

    return WordleManualGym(
        log_func=log_func,
        data_file=Path("./data/wordle/games.db"),
        config_creator=lambda: WordleConfig(
            max_guesses=int(input("Max Guesses: ")),
            game_ids=[int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))],
        ),
    )


def build_letroso_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.letroso.generators.common import LetrosoConfig
    from word_arena.games.letroso.gyms.manual import LetrosoManualGym

    return LetrosoManualGym(
        log_func=log_func,
        data_file=Path("./data/letroso/games.db"),
        config_creator=lambda: LetrosoConfig(
            max_letters=int(input("Max Input Letters: ")),
            max_guesses=int(input("Max Guesses: ")),
            game_ids=[int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))],
        ),
    )


def build_conexo_manual_gym(log_func: Callable[[str], None]) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.conexo.generators.common import ConexoConfig
    from word_arena.games.conexo.gyms.manual import ConexoManualGym

    return ConexoManualGym(
        log_func=log_func,
        data_file=Path("./data/conexo/games.db"),
        config_creator=lambda: ConexoConfig(
            max_guesses=int(input("Max Guesses: ")), game_id=int(input("Game ID: "))
        ),
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
