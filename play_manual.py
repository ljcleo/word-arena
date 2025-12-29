from collections.abc import Callable
from pathlib import Path

from word_arena.common.gym.manual import BaseManualGym


def build_contexto_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.contexto.gyms.manual import ContextoExampleManualGym

    return ContextoExampleManualGym(log_func=log_func, input_func=input_func)


def build_contexto_hint_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.contexto_hint.gyms.manual import ContextoHintExampleManualGym

    return ContextoHintExampleManualGym(
        data_file=Path("./data/contexto_hint/games.db"), log_func=log_func, input_func=input_func
    )


def build_wordle_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.wordle.gyms.manual import WordleExampleManualGym

    return WordleExampleManualGym(
        data_file=Path("./data/wordle/games.db"), log_func=log_func, input_func=input_func
    )


def build_letroso_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.letroso.gyms.manual import LetrosoExampleManualGym

    return LetrosoExampleManualGym(
        data_file=Path("./data/letroso/games.db"), log_func=log_func, input_func=input_func
    )


def build_conexo_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.conexo.gyms.manual import ConexoExampleManualGym

    return ConexoExampleManualGym(
        data_file=Path("./data/conexo/games.db"), log_func=log_func, input_func=input_func
    )


def build_numberle_manual_gym(input_func: Callable[[str], str], log_func: Callable[[str], None]):
    from word_arena.games.numberle.gyms.manual import NumberleExampleManualGym

    return NumberleExampleManualGym(
        data_file=Path("./data/numberle/games.db"), log_func=log_func, input_func=input_func
    )


def build_connections_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.connections.gyms.manual import ConnectionsExampleManualGym

    return ConnectionsExampleManualGym(
        data_file=Path("./data/connections/games.db"), log_func=log_func, input_func=input_func
    )


def build_strands_manual_gym(
    input_func: Callable[[str], str], log_func: Callable[[str], None]
) -> BaseManualGym:
    from word_arena.games.strands.gyms.manual import StrandsExampleManualGym

    return StrandsExampleManualGym(
        data_file=Path("./data/strands/games.db"), log_func=log_func, input_func=input_func
    )


MANUAL_GYM_BUILDERS: dict[
    str, Callable[[Callable[[str], str], Callable[[str], None]], BaseManualGym]
] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
    "letroso": build_letroso_manual_gym,
    "conexo": build_conexo_manual_gym,
    "numberle": build_numberle_manual_gym,
    "connections": build_connections_manual_gym,
    "strands": build_strands_manual_gym,
}


def main() -> None:
    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: "))]](input, print).play(input, print)


if __name__ == "__main__":
    main()
