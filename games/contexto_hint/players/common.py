from collections.abc import Iterator
from itertools import starmap
from typing import override

from players.common import BaseIOPlayer


def index_to_option(index: int) -> str:
    return chr(ord("A") + index)


def make_option(index: int, word: str) -> str:
    return f"{index_to_option(index)}: {word}"


def make_options(*, hint: list[str]) -> str:
    return "; ".join(starmap(make_option, enumerate(hint)))


class ContextoHintIOPlayer(BaseIOPlayer[None, list[str], int, int]):
    @override
    def format_hint(self, *, hint: list[str]) -> Iterator[str]:
        yield "Candidates (Use Uppercase Letter to Guess):"
        yield make_options(hint=hint)

    @override
    def process_guess(self, *, hint: list[str], raw_guess: str) -> int:
        return ord(raw_guess) - ord("A") if len(raw_guess) == 1 else -1

    @override
    def format_feedback(self, *, hint: list[str], guess: int, feedback: int) -> Iterator[str]:
        yield (
            "Invalid Input" if feedback == -1 else f"Guess: {hint[guess]}; Position: {feedback + 1}"
        )
