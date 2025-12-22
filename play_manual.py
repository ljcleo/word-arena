from collections.abc import Callable

from word_arena.common.gym.manual import BaseManualGym


def build_contexto_manual_gym() -> BaseManualGym:
    from word_arena.games.contexto.gyms.manual import ContextoManualGym

    return ContextoManualGym()


def build_contexto_hint_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.gyms.manual import ContextoHintManualGym

    return ContextoHintManualGym(games_dir=Path("./data/contexto_hint/games"))


def build_wordle_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.wordle.gyms.manual import WordleManualGym

    return WordleManualGym(word_list_file=Path("./data/wordle/words.txt"))


def build_letroso_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.letroso.gyms.manual import LetrosoManualGym

    return LetrosoManualGym(word_list_file=Path("./data/letroso/words.txt"))


def build_conexo_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.conexo.gyms.manual import ConexoManualGym

    return ConexoManualGym(games_dir=Path("./data/conexo/games"))


MANUAL_GYM_BUILDERS: dict[str, Callable[[], BaseManualGym]] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
    "letroso": build_letroso_manual_gym,
    "conexo": build_conexo_manual_gym,
}


def main():
    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: "))]]().play(input)


if __name__ == "__main__":
    main()
