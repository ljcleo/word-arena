from typing import override

from ....common.player.log import BaseLogPlayer


class ContextoHintLogPlayer(BaseLogPlayer[None, list[str], int, int]):
    @override
    def process_guess(self, *, hint: list[str], raw_guess: str) -> int:
        return int(raw_guess) - 1 if raw_guess.isdigit() else -1
