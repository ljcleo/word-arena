from collections.abc import Callable

from ...players.manual.reader.input import StrandsInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> StrandsInputManualReader:
    return StrandsInputManualReader(input_func=input_func)
