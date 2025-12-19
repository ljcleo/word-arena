from collections.abc import Iterator
from typing import override

from games.letroso.common import LetrosoFeedback, LetrosoInfo
from players.common import BaseIOPlayer


class LetrosoIOPlayer(BaseIOPlayer[LetrosoInfo, None, str, LetrosoFeedback]):
    @override
    def format_game_info(self, *, game_info: LetrosoInfo) -> Iterator[str]:
        yield from ()

    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> str:
        return raw_guess

    @override
    def format_feedback(
        self, *, hint: None, guess: str, feedback: LetrosoFeedback
    ) -> Iterator[str]:
        yield f"Guess: {guess}; Feedback: {feedback}"
