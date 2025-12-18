from collections.abc import Iterator
from typing import override

from games.wordle.common import WordleFeedback, WordleInfo
from players.common import BaseIOPlayer


class WordleIOPlayer(BaseIOPlayer[WordleInfo, None, str, WordleFeedback]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_feedback(self, *, hint: None, guess: str, feedback: WordleFeedback) -> Iterator[str]:
        yield f"Guess: {guess}; Feedback: {feedback}"
