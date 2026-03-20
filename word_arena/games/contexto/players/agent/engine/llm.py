from collections.abc import Iterator
from typing import override

from ......players.agent.engine.llm import BaseLLMAgentEngine
from ....common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoResponse
from ..common import (
    ContextoGameRecord,
    ContextoGameStateInterface,
    ContextoNote,
    ContextoNoteStateInterface,
)

CONTEXTO_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.\
"""

CONTEXTO_GAME_RULE = """\
The game holds a word list with tens of thousands words, including the secret word, \
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word \
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet, \
related to both meaning and proximity.

Every time, you choose a word as your next guess; the word will be lemmatized to its stem form.

If the word is accepted, you will see its lemma and the lemma's position in the list, \
otherwise you will see the reject reason, such as invalid format, word not in list, or taboo words.

You should try your best to minimize the number of guesses; there may be a guessing limit.

Your guess should be a **single word with only lowercase letters and no hyphens**.\
"""


class ContextoLLMAgentEngine(
    BaseLLMAgentEngine[int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote]
):
    @property
    @override
    def guess_cls(self) -> type[ContextoGuess]:
        return ContextoGuess

    @property
    @override
    def note_cls(self) -> type[ContextoNote]:
        return ContextoNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word similarity laws and possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: ContextoGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you guessed very close or very far words."

    @override
    def get_note_example(self) -> ContextoNote:
        return ContextoNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @override
    def get_guess_example(self, *, game_state: ContextoGameStateInterface) -> ContextoGuess:
        return ContextoGuess(word="play")

    @override
    def prompt_note(self, *, note_state: ContextoNoteStateInterface) -> Iterator[tuple[str, str]]:
        yield "Word Similarity Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: ContextoGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: ContextoGameStateInterface, guess: ContextoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: ContextoGameStateInterface,
        guess: ContextoGuess,
        feedback: ContextoFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: ContextoGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: ContextoGameRecord, turn_index: int, guess: ContextoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: ContextoGameRecord,
        turn_index: int,
        guess: ContextoGuess,
        feedback: ContextoFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: ContextoGameRecord) -> Iterator[tuple[str, str]]:
        final_result: ContextoFinalResult = game_record.final_result

        if final_result.best_pos == 0:
            yield "Game Result", "Victory"
        else:
            yield "Game Result", "Failed"
            yield "Best Guess", f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield "Secret Word", final_result.top_words[0]
        yield "Top 30 Words", ", ".join(final_result.top_words[:30])

    def _prompt_game_info(self, *, game_info: int) -> Iterator[tuple[str, str]]:
        yield "Maximum Number of Guesses", "Unlimited" if game_info <= 0 else str(game_info)

    def _prompt_guess(self, *, guess: ContextoGuess) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    def _prompt_feedback(self, *, feedback: ContextoFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, ContextoResponse):
            yield "Validation Result", "Accept"
            yield "Lemma Form", feedback.lemma
            yield "Position", str(feedback.distance + 1)
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback.error
