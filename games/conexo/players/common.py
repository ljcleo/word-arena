from collections.abc import Iterator
from typing import override

from games.conexo.common import ConexoFeedback, ConexoInfo
from players.common import BaseIOPlayer


class ConexoIOPlayer(BaseIOPlayer[ConexoInfo, None, set[int], ConexoFeedback]):
    @override
    def prepare(self, *, game_info: ConexoInfo) -> None:
        super().prepare(game_info=game_info)
        self._words: list[str] = game_info.words

    @override
    def format_game_info(self, *, game_info: ConexoInfo) -> Iterator[str]:
        yield "Words (Use Index to Guess):"
        yield f"{game_info.format_options()}"

    @override
    def format_hint(self, *, hint: None) -> Iterator[str]:
        yield from ()

    @override
    def process_guess(self, *, hint: None, raw_guess: str) -> set[int]:
        return {int(guess) - 1 if guess.isdigit() else -1 for guess in raw_guess.strip().split()}

    @override
    def format_feedback(
        self, *, hint: None, guess: set[int], feedback: ConexoFeedback
    ) -> Iterator[str]:
        yield f"Guess: {', '.join(self._words[index] for index in guess)}; Feedback: {feedback}"
