from collections.abc import Callable

from ...players.manual.reader.input import NumberleInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> NumberleInputManualReader:
    return NumberleInputManualReader(input_func=input_func)
