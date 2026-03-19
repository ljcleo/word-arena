from collections.abc import Callable

from ...players.manual.reader.input import ContextoInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ContextoInputManualReader:
    return ContextoInputManualReader(input_func=input_func)
