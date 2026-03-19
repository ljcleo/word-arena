from collections.abc import Callable

from ...players.manual.reader.input import ContextoHintInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ContextoHintInputManualReader:
    return ContextoHintInputManualReader(input_func=input_func)
