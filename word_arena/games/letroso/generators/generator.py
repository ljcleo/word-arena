from collections.abc import Iterable
from random import Random
from typing import override

from ....common.generator.generator import BaseGameGenerator
from ..game import LetrosoGame
from .common import LetrosoConfig, LetrosoSetting
from .provider import LetrosoGameProvider


class LetrosoGameGenerator(
    BaseGameGenerator[LetrosoSetting, LetrosoConfig, LetrosoGame], LetrosoGameProvider
):
    @override
    def __init__(
        self, *, setting_pool: Iterable[LetrosoSetting], seed: int, word_list: Iterable[str]
    ) -> None:
        super().__init__(setting_pool=setting_pool, seed=seed)
        self._word_list: list[str] = list(word_list)
        self._num_games: int = len(self._word_list)

    @override
    def generate_config(self, *, setting: LetrosoSetting, rng: Random) -> LetrosoConfig:
        return LetrosoConfig(
            word_list=self._word_list,
            target_ids=rng.sample(range(self._num_games), setting.num_targets),
            max_letters=setting.max_letters,
            max_guesses=setting.max_guesses,
        )
