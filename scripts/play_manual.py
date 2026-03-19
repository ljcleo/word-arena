from collections.abc import Callable

from common import build_gym

from word_arena.players.manual.player import ManualPlayer
from word_arena.players.manual.reader.input import BaseInputManualReader


def build_contexto_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.contexto.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_contexto_hint_player_components(
    input_func: Callable[[str], str],
) -> BaseInputManualReader:
    from word_arena.games.contexto_hint.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_wordle_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.wordle.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_letroso_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.letroso.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_conexo_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.conexo.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_numberle_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.numberle.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_connections_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.connections.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_strands_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.strands.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_turing_player_components(input_func: Callable[[str], str]) -> BaseInputManualReader:
    from word_arena.games.turing.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


PLAYER_COMPONENT_BUILDERS: dict[str, Callable[[Callable[[str], str]], BaseInputManualReader]] = {
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


def build_player(*, game_key: str) -> ManualPlayer:
    return ManualPlayer(reader=PLAYER_COMPONENT_BUILDERS[game_key](input))


def main() -> None:
    games: list[str] = list(PLAYER_COMPONENT_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    game_key: str = games[int(input("Game Index: "))]
    build_gym(game_key=game_key).play(player=build_player(game_key=game_key))


if __name__ == "__main__":
    main()
