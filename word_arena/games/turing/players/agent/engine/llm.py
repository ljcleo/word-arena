from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from ......common.game.common import Trajectory
from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ......utils import join_or_na
from ....common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo


class TuringNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type TuringGameStateInterface = AgentGameStateInterface[
    TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult
]

type TuringNoteStateInterface = AgentNoteStateInterface[
    TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote
]

type TuringGameRecord = GameRecord[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult]


class TuringLLMAgentEngine(
    BaseLLMAgentEngine[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote]
):
    ROLE_DEFINITION = """\
You are an intelligent AI good at logic deduction.

You are playing a game where you need to find a secret code with digits.\
"""

    GAME_RULE = """\
The game holds a 3-digit secret code `xyz`, where each digit `x`, `y` and `z` ranges from 1 to 5.

Multiple verifiers (indexed from 0) are available to help you find out the secret code, \
each of which holds a boolean criterion concerning `x`, `y` and `z` \
(e.g. `x < y` or `x + y + z > 6`), and tells whether an input code satisfies that criterion.

Each verifier will show at least two candidate criteria at the beginning of the game, \
but will only use one of them for verification throughout the game, \
so you will need to figure out which criterion the verifier actually verifies.

It is satisfied that ONLY the secret code passes all verifiers, \
and all other codes will fail on some verifier(s);
furthermore, it is guaranteed that no verifier is superfluous.

Your guesses will consist of multiple verifying guesses and one last final guess.

In a verifying guess, you propose a 3-digit code, each digit ranging from 1 to 5, \
along with 1 to 3 verifier indices to which you want to input the code; \
the chosen verifiers will return yes or no according to your code and their hidden criterion.

When you believe you have figured out the secret code, you can make your final guess, \
where you propose the secret code along with an empty verifier list; \
the game then ends immediately, returning whether you have successfully find the secret code or not.

If your guess (both verifying and final) does not follow the above format, \
then the guess will be rejected, and you will see why. \

There may be a guessing limit on the total number of guesses \
(including verifying, final and rejected ones); \
therefore, you should try your best to minimize the number of guesses.

Your guess should be a **3-digit code plus a list of verifier indices \
(empty for the final guess)**.\
"""

    NOTE_CLS = TuringNote
    GUESS_CLS = TuringGuess

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: TuringGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> TuringNote:
        return TuringNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: TuringGameStateInterface) -> TuringGuess:
        return TuringGuess(code=123, verifiers=[0, 1, 2])

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: TuringInfo = trajectory.game_info

        for index, card in enumerate(game_info.verifiers):
            yield f"Verifier {index}", join_or_na(card)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        turn_index: int,
        guess: TuringGuess,
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if len(guess.verifiers) == 0:
            yield "Final Guess", str(guess.code)
        else:
            yield "Verifying Guess", str(guess.code)
            yield "Verifiers", join_or_na(map(str, guess.verifiers))

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[TuringInfo, TuringGuess, TuringFeedback],
        turn_index: int,
        guess: TuringGuess,
        feedback: TuringFeedback,
        final_result: TuringFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, list):
            yield "Validation Result", "Accept"
            yield "Verification Result", join_or_na("Y" if result else "N" for result in feedback)
        elif isinstance(feedback, bool):
            yield "Validation Result", "Accept"
            yield "Final Guess Result", "Correct" if feedback else "Incorrect"
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback

    @override
    def prompt_final_result(self, *, game_record: TuringGameRecord) -> Iterator[tuple[str, str]]:
        final_result: TuringFinalResult = game_record.final_result
        yield "Game Result", "Victory" if final_result.verdict is True else "Failed"
        yield "Asked Questions", str(final_result.num_questions)
        yield "Made Final Guess", "Yes" if final_result.verdict is not None else "No"
        yield "Secret Code", str(final_result.answer)
