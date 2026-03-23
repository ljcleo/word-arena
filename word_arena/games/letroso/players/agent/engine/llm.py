from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ....common import (
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
    LetrosoResponse,
)


class LetrosoNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type LetrosoGameStateInterface = AgentGameStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
]

type LetrosoNoteStateInterface = AgentNoteStateInterface[
    LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote
]

type LetrosoGameRecord = GameRecord[LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]

LETROSO_ROLE_DEF = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

LETROSO_GAME_RULE = """\
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


class LetrosoLLMAgentEngine(
    BaseLLMAgentEngine[LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote]
):
    @property
    @override
    def guess_cls(self) -> type[LetrosoGuess]:
        return LetrosoGuess

    @property
    @override
    def note_cls(self) -> type[LetrosoNote]:
        return LetrosoNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield LETROSO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield LETROSO_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: LetrosoGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> LetrosoNote:
        return LetrosoNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: LetrosoGameStateInterface) -> LetrosoGuess:
        return LetrosoGuess(word="feedback")

    @override
    def prompt_game_info(
        self, *, game_state: LetrosoGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: LetrosoGameStateInterface, guess: LetrosoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: LetrosoGameStateInterface,
        guess: LetrosoGuess,
        feedback: LetrosoFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: LetrosoGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: LetrosoGameRecord, turn_index: int, guess: LetrosoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: LetrosoGameRecord,
        turn_index: int,
        guess: LetrosoGuess,
        feedback: LetrosoFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: LetrosoGameRecord) -> Iterator[tuple[str, str]]:
        final_result: LetrosoFinalResult = game_record.final_result

        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        yield (
            "Found Words",
            self._format_found_words(
                words=map(final_result.answers.__getitem__, final_result.found_indices)
            ),
        )

        yield "Secret Words", "/".join(final_result.answers)

    def _prompt_game_info(self, *, game_info: LetrosoInfo) -> Iterator[tuple[str, str]]:
        yield "Number of Secret Words", str(game_info.num_targets)
        yield "Maximum Number of Letters in One Guess", str(game_info.max_letters)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(self, *, guess: LetrosoGuess) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    def _prompt_feedback(self, *, feedback: LetrosoFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, LetrosoResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    def _format_found_words(self, *, words: Iterable[str]) -> str:
        result: str = ", ".join(words)
        return "N/A" if result == "" else result
