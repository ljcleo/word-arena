from collections.abc import Iterator
from typing import override

from games.wordle.common import WordleInfo, WordleResult, format_wordle_result
from players.manual import BaseManualPlayer


class WordleManualPlayer(BaseManualPlayer[WordleInfo, None, str, WordleResult]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_result(self, *, hint: None, guess: str, result: WordleResult) -> Iterator[str]:
        yield f"Guess: {guess}; Result: {format_wordle_result(result)}"
