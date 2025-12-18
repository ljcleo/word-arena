from collections.abc import Iterator
from typing import override

from games.letroso.common import LetrosoInfo, LetrosoResult
from players.manual import BaseManualPlayer


class LetrosoManualPlayer(BaseManualPlayer[LetrosoInfo, None, str, LetrosoResult]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_result(self, *, hint: None, guess: str, result: LetrosoResult) -> Iterator[str]:
        yield f"Guess: {guess}; Result: {result}"
