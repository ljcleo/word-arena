from collections.abc import Callable
from typing import override

from ....common.gym.base import BaseConfigGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..formatters.base import WordleFinalResultFormatter
from ..generators.common import WordleConfig


class WordleConfigGym[**P](
    BaseConfigGym[
        WordleConfig, WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, P
    ],
    WordleFinalResultFormatter,
):
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        config_creator: Callable[[], WordleConfig],
        **kwargs,
    ) -> None:
        super().__init__(log_func=log_func, **kwargs)
        self._config_creator: Callable[[], WordleConfig] = config_creator

    @override
    def create_config(self) -> WordleConfig:
        return self._config_creator()
