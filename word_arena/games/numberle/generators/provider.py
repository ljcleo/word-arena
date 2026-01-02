from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import NumberleGame
from .common import NumberleConfig, NumberleMetaConfig


class NumberleGameProvider(BaseGameProvider[NumberleMetaConfig, NumberleConfig, NumberleGame]):
    @override
    def create_game(
        self, *, meta_config: NumberleMetaConfig, config: NumberleConfig
    ) -> NumberleGame:
        return NumberleGame(
            eq_list=meta_config.eq_list,
            target_ids=config.game_ids,
            eq_length=config.eq_length,
            max_guesses=config.max_guesses,
        )
