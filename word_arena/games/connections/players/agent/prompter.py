from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from .....common.game.common import Trajectory
from .....players.agent.prompter.base import BaseAgentPrompter
from .....utils import join_or_na
from ...common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsWordGroup,
)


class ConnectionsNote(BaseModel):
    law: str = Field(title="Word Group Laws")
    strategy: str = Field(title="Possible Strategies")


class ConnectionsAgentPrompter(
    BaseAgentPrompter[
        ConnectionsNote,
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
    ]
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

    NOTE_CLS = ConnectionsNote
    NOTE_DETAIL = "Your notes should cover empirical word group laws and possible strategies."

    NOTE_EXAMPLE = ConnectionsNote(
        law="...", strategy="Follow these rules and strategies when guessing: ..."
    )

    GUESS_CLS = ConnectionsGuess
    REFLECT_DETAIL = "Pay attention to the rounds where you successfully found a group."

    @override
    def get_guess_detail(
        self, *, trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback]
    ) -> str:
        example: range = range(trajectory.game_info.group_size)
        choices: str = join_or_na(trajectory.game_info.words[index] for index in example)
        response: str = join_or_na(map(str, example))

        return (
            "Pay attention to the number of remaining guesses.\n\n"
            f"For example, reply {response} if you choose {choices}."
        )

    @override
    def get_guess_example(
        self, *, trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback]
    ) -> ConnectionsGuess:
        return ConnectionsGuess(indices=list(range(trajectory.game_info.group_size)))

    @override
    def prompt_game_info(
        self,
        *,
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        final_result: ConnectionsFinalResult | None,
    ) -> Iterator[tuple[str, str]]:
        game_info: ConnectionsInfo = trajectory.game_info

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
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        turn_id: int,
        guess: ConnectionsGuess,
        final_result: ConnectionsFinalResult | None,
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
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        turn_id: int,
        guess: ConnectionsGuess,
        feedback: ConnectionsFeedback,
        final_result: ConnectionsFinalResult | None,
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
    def prompt_final_result(
        self,
        *,
        trajectory: Trajectory[ConnectionsInfo, ConnectionsGuess, ConnectionsFeedback],
        final_result: ConnectionsFinalResult,
    ) -> Iterator[tuple[str, str]]:
        yield "Game Result", "Victory" if len(final_result.remaining_groups) == 0 else "Failed"
        yield "Found Groups", self._format_groups(groups=final_result.found_groups)

        if len(final_result.remaining_groups) > 0:
            yield "Groups Not Found", self._format_groups(groups=final_result.remaining_groups)

    def _format_groups(self, *, groups: Iterable[ConnectionsWordGroup]) -> str:
        return join_or_na(f"{'/'.join(group.words)} ({group.theme})" for group in groups)
