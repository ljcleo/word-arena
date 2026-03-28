from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter
from .....utils import join_or_na
from ...common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


class NumberleAgentPrompter(
    BaseAgentPrompter[
        NumberleNote, NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
    ]
):
    ROLE_DEFINITION = """\
You are an intelligent AI good at basic arithmetics.

You are playing a game where you need to find one or more secret equations.\
"""

    GAME_RULE = """\
All secret equations have the same number of characters, with both hand sides \
basic arithmetic expressions containing digits and `+-*/` only, connected by a single `=`; \
brackets, negative numbers, decimals, leading zeros, and zero divisions are NOT allowed.

Every time, you choose an equation as your next guess; the guess should be a valid equation \
following the same length and format constraints described above, **without any whitespaces**.

If the equation is accepted, you will see how \
it matches each secret equation through a labeling string:

A `G` label means that the character at that position is correct; \
a `Y` label means that the character at that position should be at somewhere else; \
a `.` means that the character is not in the secret equation, or has appeared too many times.

If the equation is rejected, you will see the reason, which shall be invalid format.

A secret equation is considered found if and only if the equation is actually guessed in a turn, \
so you will need at least as many guesses as there are secret equations to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all secret equations; \
therefore, you should try your best to minimize the number of guesses.

Your guess should be a \
**single equation obeying the length and format constraints without any whitespaces**.\
"""

    NOTE_CLS = NumberleNote
    NOTE_DETAIL = "Your notes should cover possible strategies."
    NOTE_EXAMPLE = NumberleNote(strategy="Follow these strategies when guessing: ...")
    GUESS_CLS = NumberleGuess
    REFLECT_DETAIL = "Pay attention to the rounds where you had little information gain."

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback]
    ) -> str:
        return "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback]
    ) -> NumberleGuess:
        return NumberleGuess(equation="5-4*3/2+1=0")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: NumberleInfo = trajectory.game_info
        yield "Number of Secret Equations", str(game_info.num_targets)
        yield "Equation Length in Characters", str(game_info.eq_length)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        turn_id: int,
        guess: NumberleGuess,
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Equation", guess.equation

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        turn_id: int,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
        final_result: NumberleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, NumberleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", join_or_na(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "invalid guess"

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[NumberleInfo, NumberleGuess, NumberleFeedback],
        final_result: NumberleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Equations",
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield "Secret Equations", join_or_na(final_result.answers)
