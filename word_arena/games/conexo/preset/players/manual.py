from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import ConexoGuess
from ...players.manual.reader.input import ConexoInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[ConexoGuess]] = make_input_reader(
    reader_cls=ConexoInputManualReader
)
