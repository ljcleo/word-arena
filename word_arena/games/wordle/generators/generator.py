from collections.abc import Iterable
from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import WordleGame
from .common import WordleConfig, WordleSetting
from .provider import WordleGameProvider


class WordleGameGenerator(
    BaseGameGenerator[WordleSetting, WordleConfig, WordleGame], WordleGameProvider
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[WordleSetting], seed: int, word_list: Iterable[str]
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        self._word_list: list[str] = list(word_list)
        self._num_games: int = len(self._word_list)

    @override
    def generate_config(self, *, setting: WordleSetting, rng: Random) -> WordleConfig:
        return WordleConfig(
            word_list=self._word_list,
            target_ids=rng.sample(range(self._num_games), setting.num_targets),
            max_guesses=setting.max_guesses,
        )
