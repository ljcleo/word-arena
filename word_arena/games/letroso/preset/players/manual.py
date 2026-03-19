from collections.abc import Callable

from ...players.manual.reader.input import LetrosoInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> LetrosoInputManualReader:
    return LetrosoInputManualReader(input_func=input_func)
