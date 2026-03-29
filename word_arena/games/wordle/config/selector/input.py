from collections.abc import Callable
from typing import override

from .....common.config.selector.input import BaseInputConfigSelector
from ...common import WordleConfig
from ..common import WordleMetaConfig


class WordleInputConfigSelector(BaseInputConfigSelector[WordleMetaConfig, WordleConfig]):
    @override
    def input_config(
        self, *, meta_config: WordleMetaConfig, input_func: Callable[[str], str]
    ) -> WordleConfig:
        return WordleConfig(
            word_pool=meta_config.word_pool,
            max_turns=int(input_func("Max Guesses: ")),
            game_ids=meta_config.select_game_ids(
                selector=lambda n: (
                    int(input_func(f"Word ID {i + 1} (0--{n - 1}): "))
                    for i in range(int(input_func("Num Targets: ")))
                )
            ),
        )
