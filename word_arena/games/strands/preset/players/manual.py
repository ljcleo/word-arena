from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import StrandsGuess
from ...players.manual.reader.input import StrandsInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[StrandsGuess]] = make_input_reader(
    reader_cls=StrandsInputManualReader
)
