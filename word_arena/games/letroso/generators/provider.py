from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import LetrosoGame
from .common import LetrosoConfig, LetrosoMetaConfig


class LetrosoGameProvider(BaseGameProvider[LetrosoMetaConfig, LetrosoConfig, LetrosoGame]):
    @override
    def create_game(self, *, meta_config: LetrosoMetaConfig, config: LetrosoConfig) -> LetrosoGame:
        return LetrosoGame(
            word_list=meta_config.word_list,
            target_ids=config.game_ids,
            max_letters=config.max_letters,
            max_guesses=config.max_guesses,
        )
