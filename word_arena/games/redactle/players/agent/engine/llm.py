from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
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

REDACTLE_ROLE_DEF = """\
You are an intelligent AI with broad general knowledge spanning multiple domains.

You are playing a game where you must identify the title of a hidden Wikipedia article.\
"""

REDACTLE_GAME_RULE = """\
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


class RedactleLLMAgentEngine(
    BaseLLMAgentEngine[
        RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote
    ]
):
    @property
    @override
    def guess_cls(self) -> type[RedactleGuess]:
        return RedactleGuess

    @property
    @override
    def note_cls(self) -> type[RedactleNote]:
        return RedactleNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield REDACTLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield REDACTLE_GAME_RULE

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
    def get_note_example(self) -> RedactleNote:
        return RedactleNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: RedactleGameStateInterface) -> RedactleGuess:
        return RedactleGuess(word="history")

    @override
    def prompt_note(self, *, note_state: RedactleNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: RedactleGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(
            game_info=game_state.game_info,
            feedback_history=[turn.feedback for turn in game_state.turns],
        )

    @override
    def prompt_guess(
        self, *, game_state: RedactleGameStateInterface, guess: RedactleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: RedactleGameStateInterface,
        guess: RedactleGuess,
        feedback: RedactleFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: RedactleGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(
            game_info=game_record.trajectory.game_info, feedback_history=None
        )

    @override
    def prompt_guess_final(
        self, *, game_record: RedactleGameRecord, turn_index: int, guess: RedactleGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: RedactleGameRecord,
        turn_index: int,
        guess: RedactleGuess,
        feedback: RedactleFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: RedactleGameRecord) -> Iterator[tuple[str, str]]:
        final_result: RedactleFinalResult = game_record.final_result

        yield (
            "Game Result",
            "Victory"
            if len(final_result.found_words) == len(final_result.title_words)
            else "Failed",
        )

        yield ("Found Words", self._format_items(items=final_result.found_words))
        yield "Article Title", final_result.title
        yield ("Title Words", self._format_items(items=final_result.title_words))
        yield (
            "Full Article",
            self._format_article(game_info=game_record.trajectory.game_info, feedback_history=None),
        )

    def _prompt_game_info(
        self, *, game_info: RedactleInfo, feedback_history: Iterable[RedactleFeedback] | None
    ) -> Iterator[tuple[str, str]]:
        if feedback_history is not None:
            yield (
                "Current Article",
                self._format_article(game_info=game_info, feedback_history=feedback_history),
            )

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(self, *, guess: RedactleGuess) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    def _prompt_feedback(self, *, feedback: RedactleFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, RedactleResponse):
            yield "Validation Result", "Accept"
            yield "Lemma", feedback.lemma

            yield (
                "Positions",
                self._format_items(
                    items=(
                        f"L{line_index}:{word_index}"
                        for line_index, word_index in feedback.positions
                    )
                ),
            )
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error

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

    def _format_items(self, *, items: Iterable[str]) -> str:
        result: str = ", ".join(items)
        return "N/A" if result == "" else result
