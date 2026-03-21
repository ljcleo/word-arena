from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import ContextoGuess
from ...players.manual.reader.input import ContextoInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[ContextoGuess]] = make_input_reader(
    reader_cls=ContextoInputManualReader
)
