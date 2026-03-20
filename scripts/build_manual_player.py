from collections.abc import Callable

from word_arena.players.manual.player import ManualPlayer


def build_contexto_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.contexto.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_contexto_hint_player(
    input_func: Callable[[str], str],
) -> ManualPlayer:
    from word_arena.games.contexto_hint.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_wordle_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.wordle.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_letroso_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.letroso.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_conexo_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.conexo.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_numberle_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.numberle.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_connections_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.connections.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_strands_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.strands.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_turing_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.turing.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


def build_redactle_player(input_func: Callable[[str], str]) -> ManualPlayer:
    from word_arena.games.redactle.preset.players.manual import input_reader

    return input_reader(input_func=input_func)


PLAYER_BUILDERS: dict[str, Callable[[Callable[[str], str]], ManualPlayer]] = {
    "contexto": build_contexto_player,
    "contexto-hint": build_contexto_hint_player,
    "wordle": build_wordle_player,
    "letroso": build_letroso_player,
    "conexo": build_conexo_player,
    "numberle": build_numberle_player,
    "connections": build_connections_player,
    "strands": build_strands_player,
    "turing": build_turing_player,
    "redactle": build_redactle_player,
}


def build_player(*, game_key: str) -> ManualPlayer:
    return PLAYER_BUILDERS[game_key](input)
