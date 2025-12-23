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
        self,
        *,
        setting_pool: Iterable[WordleSetting],
        seed: int,
        word_list: Iterable[str],
        game_word_list: Iterable[str],
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        self._word_list: list[str] = list(word_list)
        word_map: dict[str, int] = {word: index for index, word in enumerate(self._word_list)}
        self._target_pool: list[int] = [word_map[word] for word in game_word_list]
        self._num_games: int = len(self._target_pool)

    @override
    def generate_config(self, *, setting: WordleSetting, rng: Random) -> WordleConfig:
        return WordleConfig(
            word_list=self._word_list,
            target_ids=[
                self._target_pool[i]
                for i in rng.sample(range(self._num_games), setting.num_targets)
            ],
            max_guesses=setting.max_guesses,
        )
