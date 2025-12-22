from collections.abc import Callable
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..generators.common import WordleConfig
from ..generators.provider import WordleGameProvider
from ..players.manual import WordleManualPlayer
from .base import WordleConfigGym


class WordleManualGym(
    BaseManualGym[WordleConfig, WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult],
    WordleConfigGym[[Callable[[str], str]]],
):
    def __init__(self, *, create_config_func: Callable[[], WordleConfig]) -> None:
        super().__init__(game_provider=WordleGameProvider(), create_config_func=create_config_func)

    @override
    def create_player(self, *, input_func: Callable[[str], str]) -> WordleManualPlayer:
        return WordleManualPlayer(input_func=input_func)
