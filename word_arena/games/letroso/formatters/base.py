from collections.abc import Iterable, Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import (
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
    LetrosoResponse,
)


class LetrosoInGameFormatter(BaseInGameFormatter[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: LetrosoInfo) -> Iterator[tuple[str, str]]:
        yield "Number of Secret Words", str(game_info.num_targets)
        yield "Maximum Number of Letters in One Guess", str(game_info.max_letters)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_guesses <= 0 else str(game_info.max_guesses),
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: LetrosoInfo, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: LetrosoInfo, hint: None, guess: LetrosoGuess
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: LetrosoInfo, hint: None, guess: LetrosoGuess, feedback: LetrosoFeedback
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, LetrosoResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error


class LetrosoFinalResultFormatter(BaseFinalResultFormatter[LetrosoFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: LetrosoFinalResult) -> Iterator[tuple[str, str]]:
        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Words",
            cls._format_found_words(
                words=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Words", "/".join(final_result.answers)

    @classmethod
    def _format_found_words(cls, *, words: Iterable[str]) -> str:
        result: str = ", ".join(words)
        return "N/A" if result == "" else result
