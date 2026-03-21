from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import NumberleGuess
from ...players.manual.reader.input import NumberleInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[NumberleGuess]] = make_input_reader(
    reader_cls=NumberleInputManualReader
)
