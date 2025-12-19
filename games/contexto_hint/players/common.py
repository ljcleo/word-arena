from collections.abc import Iterator
from typing import override

from players.common import BaseIOPlayer


def format_options(*, hint: list[str]) -> str:
    return "; ".join(f"{index + 1}: {word}" for index, word in enumerate(hint))


class ContextoHintIOPlayer(BaseIOPlayer[None, list[str], int, int]):
    @override
    def format_game_info(self, *, game_info: None) -> Iterator[str]:
        yield from ()

    @override
    def format_hint(self, *, hint: list[str]) -> Iterator[str]:
        yield "Candidates (Use Index to Guess):"
        yield format_options(hint=hint)

    @override
    def process_guess(self, *, hint: list[str], raw_guess: str) -> int:
        return int(raw_guess) - 1 if raw_guess.isdigit() else -1

    @override
    def format_feedback(self, *, hint: list[str], guess: int, feedback: int) -> Iterator[str]:
        yield (
            "Invalid Input" if feedback == -1 else f"Guess: {hint[guess]}; Position: {feedback + 1}"
        )
