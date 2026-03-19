from collections.abc import Iterable, Iterator
from typing import override

from ......players.agent.engine.llm import BaseLLMAgentEngine
from ....common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsWordGroup,
)
from ..common import (
    ConnectionsGameRecord,
    ConnectionsGameStateInterface,
    ConnectionsNote,
    ConnectionsNoteStateInterface,
)

CONNECTIONS_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find the groups behind words.\
"""

CONNECTIONS_GAME_RULE = """\
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


class ConnectionsLLMAgentEngine(
    BaseLLMAgentEngine[
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
    ]
):
    @property
    @override
    def guess_cls(self) -> type[ConnectionsGuess]:
        return ConnectionsGuess

    @property
    @override
    def note_cls(self) -> type[ConnectionsNote]:
        return ConnectionsNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word group laws and possible strategies."

    @override
    def make_guess_detail_prompt(
        self, *, game_state: ConnectionsGameStateInterface
    ) -> Iterator[str]:
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
    def get_note_example(self) -> ConnectionsNote:
        return ConnectionsNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )

    @override
    def get_guess_example(self, *, game_state: ConnectionsGameStateInterface) -> ConnectionsGuess:
        return ConnectionsGuess(indices=list(range(game_state.game_info.group_size)))

    @override
    def prompt_note(
        self, *, note_state: ConnectionsNoteStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield "Word Group Laws", note_state.note.law
        yield "Possible Strategies", note_state.note.strategy

    @override
    def prompt_game_info(
        self, *, game_state: ConnectionsGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: ConnectionsGameStateInterface, guess: ConnectionsGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_state.game_info, guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: ConnectionsGameStateInterface,
        guess: ConnectionsGuess,
        feedback: ConnectionsFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: ConnectionsGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: ConnectionsGameRecord, turn_index: int, guess: ConnectionsGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_record.trajectory.game_info, guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: ConnectionsGameRecord,
        turn_index: int,
        guess: ConnectionsGuess,
        feedback: ConnectionsFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(
        self, *, game_record: ConnectionsGameRecord
    ) -> Iterator[tuple[str, str]]:
        final_result: ConnectionsFinalResult = game_record.final_result
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", self._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield ("Groups Not Found", self._format_groups(groups=final_result.remaining_groups))

    def _prompt_game_info(self, *, game_info: ConnectionsInfo) -> Iterator[tuple[str, str]]:
        yield "Words", "; ".join(f"{index}. {word}" for index, word in enumerate(game_info.words))
        yield "Group Size", str(game_info.group_size)

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(
        self, *, game_info: ConnectionsInfo, guess: ConnectionsGuess
    ) -> Iterator[tuple[str, str]]:
        yield (
            "Selected Words",
            ", ".join(
                self._format_guess_index(words=game_info.words, index=index)
                for index in guess.indices
            ),
        )

    def _prompt_feedback(self, *, feedback: ConnectionsFeedback) -> Iterator[tuple[str, str]]:
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

    def _format_groups(self, *, groups: Iterable[ConnectionsWordGroup]) -> str:
        result: str = "; ".join(f"{', '.join(group.words)} ({group.theme})" for group in groups)
        return "N/A" if result == "" else result
