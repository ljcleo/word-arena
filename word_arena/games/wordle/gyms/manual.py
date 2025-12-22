from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..generators.common import WordleConfig
from ..generators.provider import WordleGameProvider
from ..players.manual import WordleManualPlayer
from .base import WordleConfigGym


class WordleManualGym(
    BaseManualGym[WordleConfig, WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult],
    WordleConfigGym[[]],
):
    def __init__(self, *, word_list_file: Path) -> None:
        super().__init__(game_provider=WordleGameProvider())
        super(BaseManualGym, self).__init__(word_list_file=word_list_file)

    @override
    def create_player(self) -> WordleManualPlayer:
        return WordleManualPlayer()
