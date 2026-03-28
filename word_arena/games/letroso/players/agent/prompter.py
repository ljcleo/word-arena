from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter
from .....utils import join_or_na
from ...common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo


class LetrosoNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


class LetrosoAgentPrompter(
    BaseAgentPrompter[LetrosoNote, LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]
):
    ROLE_DEFINITION = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

    GAME_RULE = """\
All secret words are selected from a large vocabulary that covers most of the English words, \
yet their lengths may vary.

Every time, you choose a word as your next guess; \
the guess should be a valid English word with no more than a specific number of letters.

If the word is accepted, you will see how it matches each secret word \
through a bracketed labeling string the same length as the guessed word:

A `G` label or `>` label means that the relative order of the letter at that position, \
compared to other `G`-labeled or `>`-labeled letters, is the same in the secret word; \
however, its absolute position in the secret word can be different.

A `Y` label means that the letter at that position appears in the secret word, \
but its relative order, compared to `G`-labeled or `>`-labeled letters, is incorrect; \
a `.` label means that the letter is not in the secret word, or appears too many times.

Furthermore, `>` always appears right after `G` or `>`, forming a `G`-sequence like `G>>>`, \
meaning that the corresponding letters appear together in the secret word, adjacent to each other.

Directly adjacent `G`-sequences are NOT adjacent to each other in the secret word: \
for example, `GG` (NOT `G>`) means that the two adjacent letters in the guessed word \
are NOT adjacent in the secret word, though the relative order is correct; \
however, this does not apply to non-directly adjacent `G`-sequences like in `GYG`.

The default brackets are `[` and `]`, \
and `(` at the beginning means that the secret word starts with the first `G`-sequence, \
while `)` at the end means that the secret word ends with the last `G`-sequence; \
therefore, the secret word itself will be labeled like `(G>>>>)`.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn, \
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all secret words; \
therefore, you should try your best to minimize the number of guesses.

Your guess should be a **single word with only lowercase letters within the length constraint**.\
"""

    NOTE_CLS = LetrosoNote
    NOTE_DETAIL = "Your notes should cover possible strategies."
    NOTE_EXAMPLE = LetrosoNote(strategy="Follow these strategies when guessing: ...")
    GUESS_CLS = LetrosoGuess
    REFLECT_DETAIL = "Pay attention to the rounds where you had little information gain."

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback]
    ) -> str:
        return "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback]
    ) -> LetrosoGuess:
        return LetrosoGuess(word="feedback")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: LetrosoInfo = trajectory.game_info
        yield "Number of Secret Words", str(game_info.num_targets)
        yield "Maximum Number of Letters in One Guess", str(game_info.max_letters)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        turn_id: int,
        guess: LetrosoGuess,
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        turn_id: int,
        guess: LetrosoGuess,
        feedback: LetrosoFeedback,
        final_result: LetrosoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, list):
            yield "Validation Result", "Accept"
            yield "Match Pattern", join_or_na(feedback)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "unknown word" if feedback else "invalid guess"

    @override
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[LetrosoInfo, LetrosoGuess, LetrosoFeedback],
        final_result: LetrosoFinalResult,
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
