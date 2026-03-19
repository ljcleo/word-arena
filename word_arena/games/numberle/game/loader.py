from typing import override

from ....common.game.loader.base import BaseGameLoader
from ..common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo
from .common import NumberleConfig
from .engine import NumberleGameEngine


class NumberleGameLoader(
    BaseGameLoader[
        NumberleConfig, NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
    ]
):
    @override
    def create_engine(self, *, config: NumberleConfig) -> NumberleGameEngine:
        return NumberleGameEngine(
            eq_pool=config.eq_pool,
            target_ids=config.game_ids,
            eq_length=config.eq_length,
            max_turns=config.max_turns,
        )
