from collections.abc import Iterator
from typing import override

from games.contexto.common import ContextoResult, format_contexto_result
from players.manual import BaseManualPlayer


class ContextoManualPlayer(BaseManualPlayer[int, None, str, ContextoResult]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_result(self, *, hint: None, guess: str, result: ContextoResult) -> Iterator[str]:
        yield f"Guess: {guess}; Result: {format_contexto_result(result)}"
