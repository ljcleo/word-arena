from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
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

TURING_ROLE_DEF = """\
You are an intelligent AI good at logic deduction.

You are playing a game where you need to find a secret code with digits.\
"""

TURING_GAME_RULE = """\
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


class TuringLLMAgentEngine(
    BaseLLMAgentEngine[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote]
):
    @property
    @override
    def guess_cls(self) -> type[TuringGuess]:
        return TuringGuess

    @property
    @override
    def note_cls(self) -> type[TuringNote]:
        return TuringNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield TURING_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield TURING_GAME_RULE

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
        self, *, game_state: TuringGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: TuringGameStateInterface, guess: TuringGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self, *, game_state: TuringGameStateInterface, guess: TuringGuess, feedback: TuringFeedback
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(self, *, game_record: TuringGameRecord) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: TuringGameRecord, turn_index: int, guess: TuringGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: TuringGameRecord,
        turn_index: int,
        guess: TuringGuess,
        feedback: TuringFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: TuringGameRecord) -> Iterator[tuple[str, str]]:
        final_result: TuringFinalResult = game_record.final_result
        yield "Game Result", "Victory" if final_result.verdict is True else "Failed"
        yield "Asked Questions", str(final_result.num_questions)
        yield "Made Final Guess", "Yes" if final_result.verdict is not None else "No"
        yield "Secret Code", str(final_result.answer)

    def _prompt_game_info(self, *, game_info: TuringInfo) -> Iterator[tuple[str, str]]:
        for index, card in enumerate(game_info.verifiers):
            yield f"Verifier {index}", " ; ".join(card)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(self, *, guess: TuringGuess) -> Iterator[tuple[str, str]]:
        if len(guess.verifiers) == 0:
            yield "Final Guess", str(guess.code)
        else:
            yield "Verifying Guess", str(guess.code)
            yield "Verifiers", "/".join(map(str, guess.verifiers))

    def _prompt_feedback(self, *, feedback: TuringFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, list):
            yield "Validation Result", "Accept"
            yield "Verification Result", "/".join("Y" if result else "N" for result in feedback)
        elif isinstance(feedback, bool):
            yield "Validation Result", "Accept"
            yield "Final Guess Result", "Correct" if feedback else "Incorrect"
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback
