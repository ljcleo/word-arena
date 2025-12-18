from collections.abc import Iterator
from typing import override

from players.manual import BaseManualPlayer


class ContextoHintManualPlayer(BaseManualPlayer[None, list[str], int, int]):
    @override
    def format_hint(self, *, hint: list[str]) -> Iterator[str]:
        yield "Candidates (Use Uppercase Letter to Guess):"
        yield "; ".join(f"{chr(ord('A') + index)}: {word}" for index, word in enumerate(hint))

    @override
    def process_guess(self, *, hint: list[str], raw_guess: str) -> int:
        return ord(raw_guess) - ord("A") if len(raw_guess) == 1 else -1

    @override
    def format_result(self, *, hint: list[str], guess: int, result: int) -> Iterator[str]:
        yield "Invalid Input" if result == -1 else f"Guess: {hint[guess]}; Position: {result + 1}"
