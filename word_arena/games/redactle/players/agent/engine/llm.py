from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......common.game.common import Trajectory
from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ......utils import join_or_na
from ....common import (
    RedactleFeedback,
    RedactleFinalResult,
    RedactleGuess,
    RedactleInfo,
    RedactleResponse,
)


class RedactleNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type RedactleGameStateInterface = AgentGameStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
]

type RedactleNoteStateInterface = AgentNoteStateInterface[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote
]

type RedactleGameRecord = GameRecord[
    RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult
]


class RedactleLLMAgentEngine(
    BaseLLMAgentEngine[
        RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote
    ]
):
    ROLE_DEFINITION = """\
You are an intelligent AI with broad general knowledge spanning multiple domains.

You are playing a game where you must identify the title of a hidden Wikipedia article.\
"""

    GAME_RULE = """\
You are shown a Wikipedia article in English where all meaningful words are redacted, \
that is, replaced with █-characters of the same length; \
common function words (stop words) and punctuation are always visible as-is.

Every time, you receive the current article with words not found redacted, and you guess one word; \
the word can be non-English or even digits, but must be a single word.

If the word does not contain whitespaces and is not a common word in the stop word list, \
you will see the lemmatized form of the word and all related occurrences in the article, \
reported in L{line_no}:{word_pos} format; \
otherwise, the word will be rejected, and you will see the reason.

The title is considered revealed if and only if all redacted words in line 0 (L0) is guessed, \
so you will need at least as many guesses as there are unique lemmas in line 0 to win the game.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all redacted words in line 0; \
therefore, you should try your best to minimize the number of guesses.

Your guess must be a **single word (in any language) without any whitespace**.\
"""

    NOTE_CLS = RedactleNote
    NOTE_EXAMPLE = RedactleNote(strategy="Follow these strategies when guessing: ...")
    GUESS_CLS = RedactleGuess

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: RedactleGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_guess_example(self, *, game_state: RedactleGameStateInterface) -> RedactleGuess:
        return RedactleGuess(word="history")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: RedactleInfo = trajectory.game_info

        if final_result is None:
            yield (
                "Current Article",
                self._format_article(
                    game_info=game_info,
                    feedback_history=[turn.feedback for turn in trajectory.turns],
                ),
            )

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        turn_index: int,
        guess: RedactleGuess,
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[RedactleInfo, RedactleGuess, RedactleFeedback],
        turn_index: int,
        guess: RedactleGuess,
        feedback: RedactleFeedback,
        final_result: RedactleFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, RedactleResponse):
            yield "Validation Result", "Accept"
            yield "Lemma", feedback.lemma

            yield (
                "Positions",
                join_or_na(
                    f"L{line_index}:{word_index}" for line_index, word_index in feedback.positions
                ),
            )
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

    @override
    def prompt_final_result(self, *, game_record: RedactleGameRecord) -> Iterator[tuple[str, str]]:
        final_result: RedactleFinalResult = game_record.final_result

        yield (
            "Game Result",
            "Victory"
            if len(final_result.found_words) == len(final_result.title_words)
            else "Failed",
        )

        yield "Found Words", join_or_na(final_result.found_words)
        yield "Article Title", final_result.title
        yield "Title Words", join_or_na(final_result.title_words)
        yield (
            "Full Article",
            self._format_article(game_info=game_record.trajectory.game_info, feedback_history=None),
        )

    def _format_article(
        self, *, game_info: RedactleInfo, feedback_history: Iterable[RedactleFeedback] | None
    ) -> str:
        return "\n".join(
            f"{line_index}: "
            + self._format_line(
                line=line,
                visible_words=None
                if feedback_history is None
                else game_info.stop_words
                | {
                    feedback.lemma
                    for feedback in feedback_history
                    if isinstance(feedback, RedactleResponse)
                },
            )
            for line_index, line in enumerate(game_info.article)
        )

    def _format_line(
        self, *, line: list[tuple[str, str | None]], visible_words: set[str] | None
    ) -> str:
        return "".join(
            word
            if lemma is None or visible_words is None or lemma in visible_words
            else "█" * len(word)
            for word, lemma in line
        )
