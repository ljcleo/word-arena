from collections.abc import Iterable
from pathlib import Path
from random import Random
from typing import override

from pydantic import BaseModel

from ...common.game.generator import BaseGameGenerator, BaseGameProvider
from .game import WordleGame


class WordleSetting(BaseModel):
    num_targets: int
    max_guesses: int


class WordleConfig(BaseModel):
    word_list: list[str]
    target_ids: list[int]
    max_guesses: int


class WordleGameProvider(BaseGameProvider[WordleConfig, WordleGame]):
    @override
    def create_game(self, *, config: WordleConfig) -> WordleGame:
        return WordleGame(
            word_list=config.word_list, target_ids=config.target_ids, max_guesses=config.max_guesses
        )


class WordleGameGenerator(
    BaseGameGenerator[WordleSetting, WordleConfig, WordleGame], WordleGameProvider
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[WordleSetting], seed: int, word_list_file: Path
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)

    @override
    def generate_config(self, *, setting: WordleSetting, rng: Random) -> WordleConfig:
        return WordleConfig(
            word_list=self._word_list,
            target_ids=rng.sample(range(self._num_games), setting.num_targets),
            max_guesses=setting.max_guesses,
        )
