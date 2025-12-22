from collections.abc import Callable
from pathlib import Path
from typing import override

from ....common.gym.manual import BaseManualGym
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ..generators.common import LetrosoConfig
from ..generators.provider import LetrosoGameProvider
from ..players.manual import LetrosoManualPlayer
from .base import LetrosoConfigGym


class LetrosoManualGym(
    BaseManualGym[
        LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
    ],
    LetrosoConfigGym[[Callable[[str], str]]],
):
    def __init__(self, *, word_list_file: Path) -> None:
        super().__init__(game_provider=LetrosoGameProvider())
        super(BaseManualGym, self).__init__(word_list_file=word_list_file)

    @override
    def create_player(self, *, input_func: Callable[[str], str]) -> LetrosoManualPlayer:
        return LetrosoManualPlayer(input_func=input_func)
