from typing import override

from ....common.player.log import BaseLogPlayer
from ..common import ConexoFeedback, ConexoInfo


class ConexoLogPlayer(BaseLogPlayer[ConexoInfo, None, set[int], ConexoFeedback]):
    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> set[int]:
        return {int(guess) - 1 if guess.isdigit() else -1 for guess in raw_guess.strip().split()}
