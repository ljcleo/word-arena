from typing import override

from ....common.player.log import BaseLogPlayer
from ..common import LetrosoFeedback, LetrosoInfo


class LetrosoLogPlayer(BaseLogPlayer[LetrosoInfo, None, str, LetrosoFeedback]):
    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess
