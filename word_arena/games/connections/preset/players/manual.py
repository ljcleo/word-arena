from collections.abc import Callable

from ...players.manual.reader.input import ConnectionsInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ConnectionsInputManualReader:
    return ConnectionsInputManualReader(input_func=input_func)
