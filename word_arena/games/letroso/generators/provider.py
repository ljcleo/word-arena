from typing import override

from ....common.generator.provider import BaseGameProvider
from ..game import LetrosoGame
from .common import LetrosoConfig


class LetrosoGameProvider(BaseGameProvider[LetrosoConfig, LetrosoGame]):
    @override
    def create_game(self, *, config: LetrosoConfig) -> LetrosoGame:
        return LetrosoGame(
            word_list=config.word_list,
            target_ids=config.target_ids,
            max_letters=config.max_letters,
            max_guesses=config.max_guesses,
        )
