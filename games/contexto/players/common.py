from collections.abc import Iterator
from typing import override

from games.contexto.common import ContextoFeedback
from players.common import BaseIOPlayer


class ContextoIOPlayer(BaseIOPlayer[int, None, str, ContextoFeedback]):
    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_feedback(
        self, *, hint: None, guess: str, feedback: ContextoFeedback
    ) -> Iterator[str]:
        yield f"Guess: {guess}; Feedback: {feedback}"
