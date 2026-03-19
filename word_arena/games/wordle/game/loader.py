from typing import override

from ....common.game.loader.base import BaseGameLoader
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from .common import WordleConfig
from .engine import WordleGameEngine


class WordleGameLoader(
    BaseGameLoader[WordleConfig, WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]
):
    @override
    def create_engine(self, *, config: WordleConfig) -> WordleGameEngine:
        return WordleGameEngine(
            word_pool=config.word_pool, target_ids=config.game_ids, max_turns=config.max_turns
        )
