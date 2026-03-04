from collections.abc import Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo


class TuringInGameFormatter(BaseInGameFormatter[TuringInfo, None, TuringGuess, TuringFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: TuringInfo) -> Iterator[tuple[str, str]]:
        for index, card in enumerate(game_info.verifiers):
            yield f"Verifier {index}", " ; ".join(card)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_guesses <= 0 else str(game_info.max_guesses),
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: TuringInfo, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: TuringInfo, hint: None, guess: TuringGuess
    ) -> Iterator[tuple[str, str]]:
        if len(guess.verifiers) == 0:
            yield "Final Guess", str(guess.code)
        else:
            yield "Verifying Guess", str(guess.code)
            yield "Verifiers", "/".join(map(str, guess.verifiers))

    @override
    @classmethod
    def format_feedback(
        cls,
        *,
        game_info: TuringInfo,
        hint: None,
        guess: TuringGuess,
        feedback: TuringFeedback,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, list):
            yield "Validation Result", "Accept"
            yield "Verification Result", "/".join("Y" if result else "N" for result in feedback)
        elif isinstance(feedback, bool):
            yield "Validation Result", "Accept"
            yield "Final Guess Result", "Correct" if feedback else "Incorrect"
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback


class TuringFinalResultFormatter(BaseFinalResultFormatter[TuringFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: TuringFinalResult) -> Iterator[tuple[str, str]]:
        yield "Game Result", "Victory" if final_result.verdict is True else "Failed"
        yield "Asked Questions", str(final_result.num_questions)
        yield "Made Final Guess", "Yes" if final_result.verdict is not None else "No"
        yield "Secret Code", str(final_result.answer)
