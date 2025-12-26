from collections.abc import Iterable, Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleInGameFormatter(
    BaseInGameFormatter[NumberleInfo, None, NumberleGuess, NumberleFeedback]
):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: NumberleInfo) -> Iterator[tuple[str, str]]:
        yield "Number of Secret Equations", str(game_info.num_targets)
        yield "Equation Length in Characters", str(game_info.eq_length)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_guesses <= 0 else str(game_info.max_guesses),
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: NumberleInfo, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: NumberleInfo, hint: None, guess: NumberleGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Equation", guess.equation

    @override
    @classmethod
    def format_feedback(
        cls,
        *,
        game_info: NumberleInfo,
        hint: None,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, NumberleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error


class NumberleFinalResultFormatter(BaseFinalResultFormatter[NumberleFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: NumberleFinalResult) -> Iterator[tuple[str, str]]:
        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Equations",
            cls._format_found_eqs(
                eqs=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Equations", "/".join(final_result.answers)

    @classmethod
    def _format_found_eqs(cls, *, eqs: Iterable[str]) -> str:
        result: str = ", ".join(eqs)
        return "N/A" if result == "" else result
