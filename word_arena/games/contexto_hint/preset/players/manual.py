from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from ...players.manual.reader.input import ContextoHintInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ManualPlayer:
    return ManualPlayer(reader=ContextoHintInputManualReader(input_func=input_func))
