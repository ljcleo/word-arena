from collections.abc import Iterator
from typing import override

from pydantic import BaseModel, Field

from ......common.game.common import Trajectory
from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ......utils import join_or_na
from ....common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoResponse


class ContextoNote(BaseModel):
    law: str = Field(title="Word Similarity Laws")
    strategy: str = Field(title="Possible Strategies")


type ContextoGameStateInterface = AgentGameStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult
]

type ContextoNoteStateInterface = AgentNoteStateInterface[
    int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote
]

type ContextoGameRecord = GameRecord[int, ContextoGuess, ContextoFeedback, ContextoFinalResult]


class ContextoLLMAgentEngine(
    BaseLLMAgentEngine[int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote]
):
    ROLE_DEFINITION = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.\
"""

    GAME_RULE = """\
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

    NOTE_CLS = ContextoNote

    NOTE_EXAMPLE = ContextoNote(
        law="...", strategy="Follow these rules and strategies when guessing: ..."
    )

    GUESS_CLS = ContextoGuess

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
    def get_guess_example(self, *, game_state: ContextoGameStateInterface) -> ContextoGuess:
        return ContextoGuess(word="play")

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: int = trajectory.game_info
        yield "Maximum Number of Guesses", "Unlimited" if game_info <= 0 else str(game_info)

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        turn_id: int,
        guess: ContextoGuess,
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        yield "Guessed Word", guess.word

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[int, ContextoGuess, ContextoFeedback],
        turn_id: int,
        guess: ContextoGuess,
        feedback: ContextoFeedback,
        final_result: ContextoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, ContextoResponse):
            yield "Validation Result", "Accept"
            yield "Lemma Form", feedback.lemma
            yield "Position", str(feedback.distance + 1)
        else:
            yield "Validation Result", "Reject"

            yield (
                "Reason",
                "guess should only contain lowercase letters"
                if feedback.error is None
                else feedback.error,
            )

    @override
    def prompt_final_result(self, *, game_record: ContextoGameRecord) -> Iterator[tuple[str, str]]:
        final_result: ContextoFinalResult = game_record.final_result

        if final_result.best_pos == 0:
            yield "Game Result", "Victory"
        else:
            yield "Game Result", "Failed"
            yield "Best Guess", f"{final_result.best_word} ({final_result.best_pos + 1})"

        yield "Secret Word", final_result.top_words[0]
        yield "Top 30 Words", join_or_na(final_result.top_words[:30])
