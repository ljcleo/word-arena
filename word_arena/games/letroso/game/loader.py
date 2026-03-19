from typing import override

from ....common.game.loader.base import BaseGameLoader
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from .common import LetrosoConfig
from .engine import LetrosoGameEngine


class LetrosoGameLoader(
    BaseGameLoader[LetrosoConfig, LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]
):
    @override
    def create_engine(self, *, config: LetrosoConfig) -> LetrosoGameEngine:
        return LetrosoGameEngine(
            word_pool=config.word_pool,
            target_ids=config.game_ids,
            max_letters=config.max_letters,
            max_turns=config.max_turns,
        )
