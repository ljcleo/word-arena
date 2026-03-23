from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ....common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleResponse


class WordleNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type WordleGameStateInterface = AgentGameStateInterface[
    WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult
]

type WordleNoteStateInterface = AgentNoteStateInterface[
    WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote
]

type WordleGameRecord = GameRecord[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult]

WORDLE_ROLE_DEF = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

WORDLE_GAME_RULE = """\
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


class WordleLLMAgentEngine(
    BaseLLMAgentEngine[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote]
):
    @property
    @override
    def guess_cls(self) -> type[WordleGuess]:
        return WordleGuess

    @property
    @override
    def note_cls(self) -> type[WordleNote]:
        return WordleNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: WordleGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> WordleNote:
        return WordleNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: WordleGameStateInterface) -> WordleGuess:
        return WordleGuess(word="world")

    @override
    def prompt_note(self, *, note_state: WordleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: WordleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: WordleGameStateInterface, guess: WordleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self, *, game_state: WordleGameStateInterface, guess: WordleGuess, feedback: WordleFeedback
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(self, *, game_record: WordleGameRecord) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: WordleGameRecord, turn_index: int, guess: WordleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: WordleGameRecord,
        turn_index: int,
        guess: WordleGuess,
        feedback: WordleFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: WordleGameRecord) -> Iterator[tuple[str, str]]:
        final_result: WordleFinalResult = game_record.final_result

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

    def _prompt_game_info(self, *, game_info: WordleInfo) -> Iterator[tuple[str, str]]:
        yield "Number of Secret Words", str(game_info.num_targets)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(self, *, guess: WordleGuess) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    def _prompt_feedback(self, *, feedback: WordleFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, WordleResponse):
            yield "Validation Result", "Accept"
            yield "Match Pattern", "/".join(feedback.patterns)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    def _format_found_words(self, *, words: Iterable[str]) -> str:
        result: str = ", ".join(words)
        return "N/A" if result == "" else result
