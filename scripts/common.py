from collections.abc import Callable
from pathlib import Path

from word_arena.common.game.config.loader.base import BaseConfigLoader
from word_arena.common.game.loader.base import BaseGameLoader
from word_arena.common.gym.gym import Gym


def build_contexto_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.contexto.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        mutable_meta_config_pool=(50,), input_func=input_func, log_func=log_func
    )


def build_contexto_hint_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.contexto_hint.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/contexto_hint/games.db"),
        mutable_meta_config_pool=(5,),
        input_func=input_func,
        log_func=log_func,
    )


def build_wordle_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.wordle.game.common import WordleMutableMetaConfig
    from word_arena.games.wordle.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/wordle/games.db"),
        mutable_meta_config_pool=(
            WordleMutableMetaConfig(max_turns=num_targets + 5, num_targets=num_targets)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_letroso_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.letroso.game.common import LetrosoMutableMetaConfig
    from word_arena.games.letroso.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/letroso/games.db"),
        mutable_meta_config_pool=(
            LetrosoMutableMetaConfig(max_letters=10, max_turns=20, num_targets=1),
        ),
        input_func=input_func,
        log_func=log_func,
    )


def build_conexo_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.conexo.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/conexo/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_numberle_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.numberle.game.common import NumberleMutableMetaConfig
    from word_arena.games.numberle.preset.game import input_config_reader_log_renderer

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


def build_connections_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.connections.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/connections/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_strands_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.strands.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/strands/games.db"),
        mutable_meta_config_pool=(20,),
        input_func=input_func,
        log_func=log_func,
    )


def build_turing_game_components(
    input_func: Callable[[str], str], log_func: Callable[[str, str], None]
) -> tuple[BaseConfigLoader, BaseGameLoader]:
    from word_arena.games.turing.game.common import TuringMutableMetaConfig
    from word_arena.games.turing.preset.game import input_config_reader_log_renderer

    return input_config_reader_log_renderer(
        data_file=Path("./data/turing/games.db"),
        mutable_meta_config_pool=(
            TuringMutableMetaConfig(num_verifiers=num_verifiers, max_turns=num_verifiers + 2)
            for num_verifiers in range(4, 7)
        ),
        input_func=input_func,
        log_func=log_func,
    )


GYM_COMPONENT_BUILDERS: dict[
    str,
    Callable[
        [Callable[[str], str], Callable[[str, str], None]], tuple[BaseConfigLoader, BaseGameLoader]
    ],
] = {
    "contexto": build_contexto_game_components,
    "contexto-hint": build_contexto_hint_game_components,
    "wordle": build_wordle_game_components,
    "letroso": build_letroso_game_components,
    "conexo": build_conexo_game_components,
    "numberle": build_numberle_game_components,
    "connections": build_connections_game_components,
    "strands": build_strands_game_components,
    "turing": build_turing_game_components,
}


def log(key: str, value: str) -> None:
    print(f"{key}: {value}")


def build_gym(*, game_key: str) -> Gym:
    config_loader: BaseConfigLoader
    game_loader: BaseGameLoader
    config_loader, game_loader = GYM_COMPONENT_BUILDERS[game_key](input, log)
    return Gym(config_loader=config_loader, game_loader=game_loader)
