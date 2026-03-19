from collections.abc import Callable

from ...players.manual.reader.input import TuringInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> TuringInputManualReader:
    return TuringInputManualReader(input_func=input_func)
