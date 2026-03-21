from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import ContextoHintGuess
from ...players.manual.reader.input import ContextoHintInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[ContextoHintGuess]] = make_input_reader(
    reader_cls=ContextoHintInputManualReader
)
