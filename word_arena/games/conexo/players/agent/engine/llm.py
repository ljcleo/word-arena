from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......common.game.common import Trajectory
from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ......utils import join_or_na
from ....common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo, ConexoWordGroup


class ConexoNote(BaseModel):
    law: str = Field(title="Word Group Laws")
    strategy: str = Field(title="Possible Strategies")


type ConexoGameStateInterface = AgentGameStateInterface[
    ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult
]

type ConexoNoteStateInterface = AgentNoteStateInterface[
    ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote
]

type ConexoGameRecord = GameRecord[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult]


class ConexoLLMAgentEngine(
    BaseLLMAgentEngine[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote]
):
    ROLE_DEFINITION = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find the groups behind words.\
"""

    GAME_RULE = """\
The game holds several word groups of the same size; \
each group has a common theme that shall cover all words in the group, \
which can be lexical, semantic, conceptual, phrasal (can form phrases with the same word), \
or any general co-membership (e.g., work titles by the same artist).

At the beginning, the game provides the group size and words from all groups (indexed from 0), \
but not the groups themselves; it is guaranteed that each word belongs to exactly one group.

Every time, you choose as many words as the group size to form a guess, \
then you will see whether the guessed words belong to the same group or not; \
if yes, then the group is considered found.

If you guess an incorrect number of words, or guess words that already belong to a found group, \
then the guess will be rejected.

There may be a limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all word groups; \
therefore, you should try your best to minimize the number of guesses.

Your guess should be the **indices of the guessed words**, NOT the words themselves.\
"""

    NOTE_CLS = ConexoNote
    GUESS_CLS = ConexoGuess

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word group laws and possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: ConexoGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        example: range = range(game_state.game_info.group_size)

        yield (
            f"For example, reply {join_or_na(map(str, example))} if you choose "
            f"{join_or_na(game_state.game_info.words[index] for index in example)}."
        )

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you successfully found a group."

    @override
    def get_note_example(self) -> ConexoNote:
        return ConexoNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @override
    def get_guess_example(self, *, game_state: ConexoGameStateInterface) -> ConexoGuess:
        return ConexoGuess(indices=list(range(game_state.game_info.group_size)))

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: ConexoInfo = trajectory.game_info

        yield (
            "Words",
            join_or_na(f"{index}. {word}" for index, word in enumerate(game_info.words)),
        )

        yield "Group Size", str(game_info.group_size)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        turn_index: int,
        guess: ConexoGuess,
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        words: list[str] = trajectory.game_info.words

        yield (
            "Selected Words",
            join_or_na(
                f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"
                for index in guess.indices
            ),
        )

    @override
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[ConexoInfo, ConexoGuess, ConexoFeedback],
        turn_index: int,
        guess: ConexoGuess,
        feedback: ConexoFeedback,
        final_result: ConexoFinalResult | None,
    ) -> Iterator[tuple[str, str]]:

        message: str | None = feedback.message

        if feedback.accepted:
            yield "Validation Result", "Accept"

            if message is None:
                yield "Is Same Group", "No"
            else:
                yield "Is Same Group", "Yes"
                yield "Theme", message
        else:
            yield "Validation Result", "Reject"
            yield "Reason", "N/A" if message is None else message

    @override
    def prompt_final_result(self, *, game_record: ConexoGameRecord) -> Iterator[tuple[str, str]]:
        final_result: ConexoFinalResult = game_record.final_result
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", self._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield ("Groups Not Found", self._format_groups(groups=final_result.remaining_groups))

    def _format_groups(self, *, groups: Iterable[ConexoWordGroup]) -> str:
        return "; ".join(f"{join_or_na(group.words)} ({group.theme})" for group in groups)
