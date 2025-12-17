from collections.abc import Iterator
from typing import override

from games.wordle.common import WordleResult
from players.manual import BaseManualPlayer


class WordleManualPlayer(BaseManualPlayer[None, None, str, WordleResult]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_result(self, *, hint: None, guess: str, result: WordleResult) -> Iterator[str]:
        if result["accepted"]:
            yield f"Guess: {guess}; Result: {result['result']}"
        else:
            yield result["result"]
