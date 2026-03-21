from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import TuringGuess
from ...players.manual.reader.input import TuringInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[TuringGuess]] = make_input_reader(
    reader_cls=TuringInputManualReader
)
