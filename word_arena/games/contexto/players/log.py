from typing import override

from ....common.player.log import BaseLogPlayer
from ..common import ContextoFeedback


class ContextoLogPlayer(BaseLogPlayer[int, None, str, ContextoFeedback]):
    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess
