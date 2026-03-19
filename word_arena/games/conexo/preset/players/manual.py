from collections.abc import Callable

from ...players.manual.reader.input import ConexoInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> ConexoInputManualReader:
    return ConexoInputManualReader(input_func=input_func)
