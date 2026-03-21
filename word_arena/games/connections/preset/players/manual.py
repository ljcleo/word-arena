from collections.abc import Callable

from .....players.manual.player import ManualPlayer
from .....players.manual.preset import make_input_reader
from ...common import ConnectionsGuess
from ...players.manual.reader.input import ConnectionsInputManualReader

input_reader: Callable[[Callable[[str], str]], ManualPlayer[ConnectionsGuess]] = make_input_reader(
    reader_cls=ConnectionsInputManualReader
)
