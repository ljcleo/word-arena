from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ....common import (
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
    NumberleResponse,
)


class NumberleNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type NumberleGameStateInterface = AgentGameStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
]

type NumberleNoteStateInterface = AgentNoteStateInterface[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote
]

type NumberleGameRecord = GameRecord[
    NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult
]

NUMBERLE_ROLE_DEF = """\
You are an intelligent AI good at basic arithmetics.

You are playing a game where you need to find one or more secret equations.\
"""

NUMBERLE_GAME_RULE = """\
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


class NumberleLLMAgentEngine(
    BaseLLMAgentEngine[
        NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote
    ]
):
    @property
    @override
    def guess_cls(self) -> type[NumberleGuess]:
        return NumberleGuess

    @property
    @override
    def note_cls(self) -> type[NumberleNote]:
        return NumberleNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield NUMBERLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield NUMBERLE_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: NumberleGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> NumberleNote:
        return NumberleNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: NumberleGameStateInterface) -> NumberleGuess:
        return NumberleGuess(equation="5-4*3/2+1=0")

    @override
    def prompt_note(self, *, note_state: NumberleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: NumberleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: NumberleGameStateInterface, guess: NumberleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: NumberleGameStateInterface,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: NumberleGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: NumberleGameRecord, turn_index: int, guess: NumberleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: NumberleGameRecord,
        turn_index: int,
        guess: NumberleGuess,
        feedback: NumberleFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: NumberleGameRecord) -> Iterator[tuple[str, str]]:
        final_result: NumberleFinalResult = game_record.final_result

        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Equations",
            self._format_found_eqs(
                eqs=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Equations", "/".join(final_result.answers)

    def _prompt_game_info(self, *, game_info: NumberleInfo) -> Iterator[tuple[str, str]]:
        yield "Number of Secret Equations", str(game_info.num_targets)
        yield "Equation Length in Characters", str(game_info.eq_length)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(self, *, guess: NumberleGuess) -> Iterator[tuple[str, str]]:
        yield "Guessed Equation", guess.equation

    def _prompt_feedback(self, *, feedback: NumberleFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, NumberleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    def _format_found_eqs(self, *, eqs: Iterable[str]) -> str:
        result: str = ", ".join(eqs)
        return "N/A" if result == "" else result
