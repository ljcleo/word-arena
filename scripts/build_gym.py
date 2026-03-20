from collections.abc import Callable
from pathlib import Path

from word_arena.common.gym.gym import Gym


def build_contexto_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.contexto.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        base_url="https://api.contexto.me/machado/en",
        mutable_meta_config_pool=(50,),
        input_func=input_func,
        log_func=log_func,
    )


def build_contexto_hint_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.contexto_hint.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/contexto_hint/games.db"),
        mutable_meta_config_pool=(5,),
        input_func=input_func,
        log_func=log_func,
    )


def build_wordle_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.wordle.config.common import WordleMutableMetaConfig
    from word_arena.games.wordle.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/wordle/games.db"),
        mutable_meta_config_pool=(
            WordleMutableMetaConfig(max_turns=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_letroso_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.letroso.config.common import LetrosoMutableMetaConfig
    from word_arena.games.letroso.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/letroso/games.db"),
        mutable_meta_config_pool=(
            LetrosoMutableMetaConfig(max_letters=10, max_turns=20, num_targets=1),
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_conexo_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.conexo.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/conexo/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_numberle_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.numberle.config.common import NumberleMutableMetaConfig
    from word_arena.games.numberle.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/numberle/games.db"),
        mutable_meta_config_pool=(
            NumberleMutableMetaConfig(
                eq_length=eq_length, max_turns=num_targets + 5, num_targets=num_targets
            )
            for eq_length in range(5, 13)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_connections_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.connections.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/connections/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_strands_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.strands.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/strands/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_turing_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.turing.config.common import TuringMutableMetaConfig
    from word_arena.games.turing.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/turing/games.db"),
        mutable_meta_config_pool=(
            TuringMutableMetaConfig(num_verifiers=num_verifiers, max_turns=num_verifiers + 2)
            for num_verifiers in range(4, 7)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_redactle_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.redactle.preset.gym import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/redactle/games.db"),
        mutable_meta_config_pool=(50,),
        input_func=input_func,
        log_func=log_func,
    )


GYM_BUILDERS: dict[str, Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]] = {
    "contexto": build_contexto_gym,
    "contexto-hint": build_contexto_hint_gym,
    "wordle": build_wordle_gym,
    "letroso": build_letroso_gym,
    "conexo": build_conexo_gym,
    "numberle": build_numberle_gym,
    "connections": build_connections_gym,
    "strands": build_strands_gym,
    "turing": build_turing_gym,
    "redactle": build_redactle_gym,
}


def build_gym(*, game_key: str) -> Gym:
    from common import log

    return GYM_BUILDERS[game_key](input, log)
