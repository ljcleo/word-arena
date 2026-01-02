from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import WordleGame
from .common import WordleConfig, WordleMetaConfig


class WordleGameProvider(BaseGameProvider[WordleMetaConfig, WordleConfig, WordleGame]):
    @override
    def create_game(self, *, meta_config: WordleMetaConfig, config: WordleConfig) -> WordleGame:
        return WordleGame(
            word_list=meta_config.word_list,
            target_ids=config.game_ids,
            max_guesses=config.max_guesses,
        )
