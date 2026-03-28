from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter
from .....utils import join_or_na
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleResponse


class WordleNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


class WordleAgentPrompter(
    BaseAgentPrompter[WordleNote, WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]
):
    ROLE_DEFINITION = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

    GAME_RULE = """\
All secret words have 5 letters, and are selected from a large vocabulary that \
covers most of the 5-letter English words.

Every time, you choose a 5-letter word as your next guess; the guess should be a valid English word.

If the word is accepted, you will see how it matches each secret word through a labeling string:

A `G` label means that the letter at that position is correct; \
a `Y` label means that the letter at that position should be at somewhere else; \
a `.` means that the letter is not in the secret word, or has appeared too many times.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn, \
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all secret words; \
therefore, you should try your best to minimize the number of guesses.

Your guess must be a **single word with 5 lowercase letters**.\
"""

    NOTE_CLS = WordleNote
    NOTE_DETAIL = "Your notes should cover possible strategies."
    NOTE_EXAMPLE = WordleNote(strategy="Follow these strategies when guessing: ...")
    GUESS_CLS = WordleGuess
    REFLECT_DETAIL = "Pay attention to the rounds where you had little information gain."

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback]
    ) -> str:
        return "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback]
    ) -> WordleGuess:
        return WordleGuess(word="world")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: WordleInfo = trajectory.game_info
        yield "Number of Secret Words", str(game_info.num_targets)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        turn_id: int,
        guess: WordleGuess,
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        turn_id: int,
        guess: WordleGuess,
        feedback: WordleFeedback,
        final_result: WordleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, WordleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", join_or_na(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "unknown word" if feedback else "invalid guess"

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[WordleInfo, WordleGuess, WordleFeedback],
        final_result: WordleFinalResult,
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Words",
            join_or_na(map(final_result.answers.__getitem__, final_result.found_indices)),
        )

        yield "Secret Words", join_or_na(final_result.answers)
