from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from ...players.manual.reader.input import ConnectionsInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ManualPlayer:
    return ManualPlayer(reader=ConnectionsInputManualReader(input_func=input_func))
