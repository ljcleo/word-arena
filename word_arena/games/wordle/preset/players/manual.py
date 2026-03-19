from collections.abc import Callable

from ...players.manual.reader.input import WordleInputManualReader


def input_reader(*, input_func: Callable[[str], str]) -> WordleInputManualReader:
    return WordleInputManualReader(input_func=input_func)
