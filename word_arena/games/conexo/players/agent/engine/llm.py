from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
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


CONEXO_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find the groups behind words.\
"""

CONEXO_GAME_RULE = """\
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


class ConexoLLMAgentEngine(
    BaseLLMAgentEngine[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote]
):
    @property
    @override
    def guess_cls(self) -> type[ConexoGuess]:
        return ConexoGuess

    @property
    @override
    def note_cls(self) -> type[ConexoNote]:
        return ConexoNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONEXO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONEXO_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word group laws and possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: ConexoGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        example: range = range(game_state.game_info.group_size)

        yield (
            f"For example, reply {', '.join(map(str, example))} if you choose "
            f"{', '.join(game_state.game_info.words[index] for index in example)}."
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
        self, *, game_state: ConexoGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: ConexoGameStateInterface, guess: ConexoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_state.game_info, guess=guess)

    @override
    def prompt_feedback(
        self, *, game_state: ConexoGameStateInterface, guess: ConexoGuess, feedback: ConexoFeedback
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(self, *, game_record: ConexoGameRecord) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: ConexoGameRecord, turn_index: int, guess: ConexoGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_record.trajectory.game_info, guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: ConexoGameRecord,
        turn_index: int,
        guess: ConexoGuess,
        feedback: ConexoFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: ConexoGameRecord) -> Iterator[tuple[str, str]]:
        final_result: ConexoFinalResult = game_record.final_result
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", self._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield ("Groups Not Found", self._format_groups(groups=final_result.remaining_groups))

    def _prompt_game_info(self, *, game_info: ConexoInfo) -> Iterator[tuple[str, str]]:
        yield "Words", "; ".join(f"{index}. {word}" for index, word in enumerate(game_info.words))
        yield "Group Size", str(game_info.group_size)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(
        self, *, game_info: ConexoInfo, guess: ConexoGuess
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Selected Words",
            ", ".join(
                self._format_guess_index(words=game_info.words, index=index)
                for index in guess.indices
            ),
        )

    def _prompt_feedback(self, *, feedback: ConexoFeedback) -> Iterator[tuple[str, str]]:
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

    def _format_guess_index(self, *, words: list[str], index: int) -> str:
        return f"{index} ({words[index] if 0 <= index < len(words) else 'N/A'})"

    def _format_groups(self, *, groups: Iterable[ConexoWordGroup]) -> str:
        result: str = "; ".join(f"{', '.join(group.words)} ({group.theme})" for group in groups)
        return "N/A" if result == "" else result
