from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import LetrosoGuess
from ...players.manual.reader.input import LetrosoInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[LetrosoGuess]] = make_input_reader(
    reader_cls=LetrosoInputManualReader
)
