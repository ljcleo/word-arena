from collections.abc import Callable
from pathlib import Path

from word_arena.common.gym.gym import Gym


def build_contexto_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.contexto.config.common import ContextoMetaConfig
    from word_arena.games.contexto.preset.gym import contexto_input_config_reader_log_game_renderer

    return contexto_input_config_reader_log_game_renderer(
        meta_config=ContextoMetaConfig(base_url="https://api.contexto.me/machado/en"),
        mutable_meta_config_pool=(50,),
        input_func=input_func,
        log_func=log_func,
    )


def build_contexto_hint_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.contexto_hint.config.common import ContextoHintMetaConfig
    from word_arena.games.contexto_hint.preset.gym import (
        contexto_hint_input_config_reader_log_game_renderer,
    )

    return contexto_hint_input_config_reader_log_game_renderer(
        meta_config=ContextoHintMetaConfig(data_file=Path("./data/contexto_hint/games.db")),
        mutable_meta_config_pool=(5,),
        input_func=input_func,
        log_func=log_func,
    )


def build_wordle_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.wordle.config.common import WordleMetaConfig, WordleMutableMetaConfig
    from word_arena.games.wordle.preset.gym import wordle_input_config_reader_log_game_renderer

    return wordle_input_config_reader_log_game_renderer(
        meta_config=WordleMetaConfig(data_file=Path("./data/wordle/games.db")),
        mutable_meta_config_pool=tuple(
            WordleMutableMetaConfig(max_turns=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_letroso_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.letroso.config.common import LetrosoMetaConfig, LetrosoMutableMetaConfig
    from word_arena.games.letroso.preset.gym import letroso_input_config_reader_log_game_renderer

    return letroso_input_config_reader_log_game_renderer(
        meta_config=LetrosoMetaConfig(data_file=Path("./data/letroso/games.db")),
        mutable_meta_config_pool=(
            LetrosoMutableMetaConfig(max_letters=10, max_turns=20, num_targets=1),
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_conexo_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.conexo.config.common import ConexoMetaConfig
    from word_arena.games.conexo.preset.gym import conexo_input_config_reader_log_game_renderer

    return conexo_input_config_reader_log_game_renderer(
        meta_config=ConexoMetaConfig(data_file=Path("./data/conexo/games.db")),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_numberle_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.numberle.config.common import (
        NumberleMetaConfig,
        NumberleMutableMetaConfig,
    )
    from word_arena.games.numberle.preset.gym import numberle_input_config_reader_log_game_renderer

    return numberle_input_config_reader_log_game_renderer(
        meta_config=NumberleMetaConfig(data_file=Path("./data/numberle/games.db")),
        mutable_meta_config_pool=tuple(
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
    from word_arena.games.connections.config.common import ConnectionsMetaConfig
    from word_arena.games.connections.preset.gym import (
        connections_input_config_reader_log_game_renderer,
    )

    return connections_input_config_reader_log_game_renderer(
        meta_config=ConnectionsMetaConfig(data_file=Path("./data/connections/games.db")),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_strands_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.strands.config.common import StrandsMetaConfig
    from word_arena.games.strands.preset.gym import strands_input_config_reader_log_game_renderer

    return strands_input_config_reader_log_game_renderer(
        meta_config=StrandsMetaConfig(data_file=Path("./data/strands/games.db")),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_turing_gym(input_func: Callable[[str], str], log_func: Callable[[str, str], None]) -> Gym:
    from word_arena.games.turing.config.common import TuringMetaConfig, TuringMutableMetaConfig
    from word_arena.games.turing.preset.gym import turing_input_config_reader_log_game_renderer

    return turing_input_config_reader_log_game_renderer(
        meta_config=TuringMetaConfig(data_file=Path("./data/turing/games.db")),
        mutable_meta_config_pool=tuple(
            TuringMutableMetaConfig(num_verifiers=num_verifiers, max_turns=num_verifiers + 2)
            for num_verifiers in range(4, 7)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_redactle_gym(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> Gym:
    from word_arena.games.redactle.config.common import RedactleMetaConfig
    from word_arena.games.redactle.preset.gym import redactle_input_config_reader_log_game_renderer

    return redactle_input_config_reader_log_game_renderer(
        meta_config=RedactleMetaConfig(data_file=Path("./data/redactle/games.db")),
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
