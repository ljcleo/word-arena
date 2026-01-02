from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..formatters.base import WordleFinalResultFormatter
from ..generators.common import WordleConfig, WordleMetaConfig


class WordleConfigGym[**P](
    BaseConfigGym[
        WordleMetaConfig,
        WordleConfig,
        WordleInfo,
        None,
        WordleGuess,
        WordleFeedback,
        WordleFinalResult,
        P,
    ],
    WordleFinalResultFormatter,
):
    pass


class WordleExampleConfigGym(WordleConfigGym):
    def __init__(
        self, *, log_func: Callable[[str], None], input_func: Callable[[str], str], **kwargs
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._input_func: Callable[[str], str] = input_func

    @override
    def create_config(self, *, meta_config: WordleMetaConfig) -> WordleConfig:
        return WordleConfig(
            max_guesses=int(self._input_func("Max Guesses: ")),
            game_ids=meta_config.select_game_ids(
                selector=lambda n: (
                    int(self._input_func(f"Word ID {i + 1} (0--{n - 1}): "))
                    for i in range(int(self._input_func("Num Targets: ")))
                )
            ),
        )
