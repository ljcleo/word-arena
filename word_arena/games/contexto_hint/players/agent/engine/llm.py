from collections.abc import Iterator
from typing import override

from ......players.agent.engine.llm import BaseLLMAgentEngine
from ....common import ContextoHintFeedback, ContextoHintGuess
from ..common import (
    ContextoHintGameRecord,
    ContextoHintGameStateInterface,
    ContextoHintNote,
    ContextoHintNoteStateInterface,
)

CONTEXTO_HINT_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.\
"""

CONTEXTO_HINT_GAME_RULE = """\
The game holds a word list with 500 words, including the secret word, \
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word \
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet, \
related to both meaning and proximity.

Every time, the game provides several candidate words (indexed from 0) from the list that \
you have not guessed before, but without their positions; \
the first round candidates are given in the game information, \
and subsequence round candidates in the feedback of the previous round.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess.

Your guess should be the **index of the guessed word**, NOT the word itself.\
"""


class ContextoHintLLMAgentEngine(
    BaseLLMAgentEngine[
        list[str], ContextoHintGuess, ContextoHintFeedback, list[str], ContextoHintNote
    ]
):
    @property
    @override
    def guess_cls(self) -> type[ContextoHintGuess]:
        return ContextoHintGuess

    @property
    @override
    def note_cls(self) -> type[ContextoHintNote]:
        return ContextoHintNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word similarity laws and possible strategies."

    @override
    def make_guess_detail_prompt(
        self, *, game_state: ContextoHintGameStateInterface
    ) -> Iterator[str]:
        choices: list[str] | None = (
            game_state.game_info
            if len(game_state.turns) == 0
            else game_state.turns[-1].feedback.next_choices
        )

        assert choices is not None
        example: int = len(choices) - 1
        yield f"For example, reply {example} if you choose {choices[example]}."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield (
            "Pay attention to the rounds where you failed to choose the word "
            "with the closest position among the candidates."
        )

    @override
    def get_note_example(self) -> ContextoHintNote:
        return ContextoHintNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @override
    def get_guess_example(self, *, game_state: ContextoHintGameStateInterface) -> ContextoHintGuess:
        choices: list[str] | None = (
            game_state.game_info
            if len(game_state.turns) == 0
            else game_state.turns[-1].feedback.next_choices
        )

        assert choices is not None
        return ContextoHintGuess(index=len(choices) - 1)

    @override
    def prompt_note(
        self, *, note_state: ContextoHintNoteStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: ContextoHintGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info, final_result=None)

    @override
    def prompt_guess(
        self, *, game_state: ContextoHintGameStateInterface, guess: ContextoHintGuess
    ) -> Iterator[tuple[str, str]]:
        choices: list[str] | None = (
            game_state.game_info
            if len(game_state.turns) == 0
            else game_state.turns[-1].feedback.next_choices
        )

        assert choices is not None
        yield from self._prompt_guess(choices=choices, guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: ContextoHintGameStateInterface,
        guess: ContextoHintGuess,
        feedback: ContextoHintFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback, final_result=None)

    @override
    def prompt_game_info_final(
        self, *, game_record: ContextoHintGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(
            game_info=game_record.trajectory.game_info, final_result=game_record.final_result
        )

    @override
    def prompt_guess_final(
        self, *, game_record: ContextoHintGameRecord, turn_index: int, guess: ContextoHintGuess
    ) -> Iterator[tuple[str, str]]:
        choices: list[str] | None = (
            game_record.trajectory.game_info
            if turn_index == 0
            else game_record.trajectory.turns[turn_index - 1].feedback.next_choices
        )

        assert choices is not None
        yield from self._prompt_guess(choices=choices, guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: ContextoHintGameRecord,
        turn_index: int,
        guess: ContextoHintGuess,
        feedback: ContextoHintFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback, final_result=game_record.final_result)

    @override
    def prompt_final_result(
        self, *, game_record: ContextoHintGameRecord
    ) -> Iterator[tuple[str, str]]:
        final_result: list[str] = game_record.final_result
        yield "Secret Word", final_result[0]
        yield "Top 30 Words", ", ".join(final_result[:30])

    def _prompt_game_info(
        self, *, game_info: list[str], final_result: list[str] | None
    ) -> Iterator[tuple[str, str]]:
        yield self._format_choices(choices=game_info, top_words=final_result, is_first=True)

    def _prompt_guess(
        self, *, choices: list[str], guess: ContextoHintGuess
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Selected Word This Round",
            self._format_guess_index(choices=choices, index=guess.index),
        )

    def _prompt_feedback(
        self, *, feedback: ContextoHintFeedback, final_result: list[str] | None
    ) -> Iterator[tuple[str, str]]:
        if feedback.distance < 0:
            yield "Validation Result", "Reject"
            yield "Reason", "Invalid guess"
        else:
            yield "Validation Result", "Accept"
            yield "Position", str(feedback.distance + 1)

        if feedback.next_choices is not None:
            yield self._format_choices(
                choices=feedback.next_choices, top_words=final_result, is_first=False
            )

    def _format_choices(
        self, *, choices: list[str], top_words: list[str] | None, is_first: bool
    ) -> tuple[str, str]:
        word_pos: dict[str, int] | None = (
            None if top_words is None else {word: pos + 1 for pos, word in enumerate(top_words)}
        )

        return f"Candidates for {'the First' if is_first else 'Next'} Round", "; ".join(
            f"{index}. {word}" if word_pos is None else f"{index}. {word} ({word_pos[word]})"
            for index, word in enumerate(choices)
        )

    def _format_guess_index(self, *, choices: list[str], index: int) -> str:
        return f"{index} ({choices[index] if 0 <= index < len(choices) else 'N/A'})"
