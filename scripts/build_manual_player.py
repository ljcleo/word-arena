from importlib import import_module

from word_arena.players.manual.player import ManualPlayer


def build_player(*, game_key: str) -> ManualPlayer:
    return import_module(f"word_arena.games.{game_key}.preset.players.manual").input_reader(input)
