from importlib import import_module

from common import make_cls_prefix

from word_arena.players.manual.player import ManualPlayer
from word_arena.players.manual.reader.input import BaseInputManualReader


def build_player(*, game_key: str) -> ManualPlayer:
    cls_prefix: str = make_cls_prefix(key=game_key)

    reader_cls: type[BaseInputManualReader] = getattr(
        import_module(f"word_arena.games.{game_key}.players.manual.reader.input"),
        f"{cls_prefix}InputManualReader",
    )

    return ManualPlayer(reader=reader_cls(input_func=input))
