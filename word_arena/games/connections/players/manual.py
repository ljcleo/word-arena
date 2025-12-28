from typing import override

from ....common.player.manual import BaseManualPlayer
from ..common import ConnectionsFeedback, ConnectionsGuess, ConnectionsInfo
from ..formatters.base import ConnectionsInGameFormatter


class ConnectionsManualPlayer(
    BaseManualPlayer[ConnectionsInfo, None, ConnectionsGuess, ConnectionsFeedback],
    ConnectionsInGameFormatter,
):
    @override
    def parse_guess(self, *, hint: None, guess_str: str) -> ConnectionsGuess:
        return ConnectionsGuess(
            indices=[int(guess) if guess.isdigit() else -1 for guess in guess_str.strip().split()]
        )
