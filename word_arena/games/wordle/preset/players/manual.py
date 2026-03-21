from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import WordleGuess
from ...players.manual.reader.input import WordleInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[WordleGuess]] = make_input_reader(
    reader_cls=WordleInputManualReader
)
