from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from ...players.manual.reader.input import RedactleInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ManualPlayer:
    return ManualPlayer(reader=RedactleInputManualReader(input_func=input_func))
