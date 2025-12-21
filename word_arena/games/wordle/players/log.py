from typing import override

from ....common.player.log import BaseLogPlayer
from ..common import WordleFeedback, WordleInfo


class WordleLogPlayer(BaseLogPlayer[WordleInfo, None, str, WordleFeedback]):
    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess
