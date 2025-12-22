from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import WordleGame
from .common import WordleConfig


class WordleGameProvider(BaseGameProvider[WordleConfig, WordleGame]):
    @override
    def create_game(self, *, config: WordleConfig) -> WordleGame:
        return WordleGame(
            word_list=config.word_list, target_ids=config.target_ids, max_guesses=config.max_guesses
        )
