from collections.abc import Callable

from .player import ManualPlayer
from .reader.input import BaseInputManualReader


def make_input_reader[GT](
    reader_cls: type[BaseInputManualReader[GT]],
) -> Callable[[Callable[[str], str]], ManualPlayer[GT]]:
    def input_reader(input_func: Callable[[str], str]) -> ManualPlayer[GT]:
        return ManualPlayer(reader=reader_cls(input_func=input_func))

    return input_reader
