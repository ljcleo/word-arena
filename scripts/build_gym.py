from collections.abc import Callable
from functools import partial
from pathlib import Path

from word_arena.common.gym.gym import Gym


def build_contexto_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.contexto.config.common import ContextoMetaConfig
    from word_arena.games.contexto.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        ContextoMetaConfig(base_url="https://api.contexto.me/machado/en"),
        (50,),
    )


def build_contexto_hint_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.contexto_hint.config.common import ContextoHintMetaConfig
    from word_arena.games.contexto_hint.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        ContextoHintMetaConfig(data_file=Path("./data/contexto_hint/games.db")),
        (5,),
    )


def build_wordle_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.wordle.config.common import WordleMetaConfig, WordleMutableMetaConfig
    from word_arena.games.wordle.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        WordleMetaConfig(data_file=Path("./data/wordle/games.db")),
        tuple(
            WordleMutableMetaConfig(max_turns=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
    )


def build_letroso_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.letroso.config.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
    from word_arena.games.letroso.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        LetrosoMetaConfig(data_file=Path("./data/letroso/games.db")),
        (LetrosoMutableMetaConfig(max_letters=10, max_turns=20, num_targets=1),),
    )


def build_conexo_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.conexo.config.common import ConexoMetaConfig
    from word_arena.games.conexo.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        ConexoMetaConfig(data_file=Path("./data/conexo/games.db")),
        (20,),
    )


def build_numberle_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.numberle.config.common import (
        NumberleMetaConfig,
        NumberleMutableMetaConfig,
    )
    from word_arena.games.numberle.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        NumberleMetaConfig(data_file=Path("./data/numberle/games.db")),
        tuple(
            NumberleMutableMetaConfig(
                eq_length=eq_length, max_turns=num_targets + 5, num_targets=num_targets
            )
            for eq_length in range(5, 13)
            for num_targets in (1, 2, 4, 8, 16)
        ),
    )


def build_connections_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.connections.config.common import ConnectionsMetaConfig
    from word_arena.games.connections.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        ConnectionsMetaConfig(data_file=Path("./data/connections/games.db")),
        (20,),
    )


def build_strands_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.strands.config.common import StrandsMetaConfig
    from word_arena.games.strands.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        StrandsMetaConfig(data_file=Path("./data/strands/games.db")),
        (20,),
    )


def build_turing_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.turing.config.common import TuringMetaConfig, TuringMutableMetaConfig
    from word_arena.games.turing.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        TuringMetaConfig(data_file=Path("./data/turing/games.db")),
        tuple(
            TuringMutableMetaConfig(num_verifiers=num_verifiers, max_turns=num_verifiers + 2)
            for num_verifiers in range(4, 7)
        ),
    )


def build_redactle_gym() -> Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]:
    from word_arena.games.redactle.config.common import RedactleMetaConfig
    from word_arena.games.redactle.preset.gym import input_config_reader_log_game_renderer

    return partial(
        input_config_reader_log_game_renderer,
        RedactleMetaConfig(data_file=Path("./data/redactle/games.db")),
        (50,),
    )


GYM_BUILDERS: dict[
    str, Callable[[], Callable[[Callable[[str], str], Callable[[str, str], None]], Gym]]
] = {
    "contexto": build_contexto_gym,
    "contexto_hint": build_contexto_hint_gym,
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

    return GYM_BUILDERS[game_key]()(input, log)
