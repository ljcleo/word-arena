from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import (
    ConnectionsFeedback,
    ConnectionsFinalResult,
    ConnectionsGuess,
    ConnectionsInfo,
    ConnectionsNote,
)
from ..formatters.agent import ConnectionsAgentMemoryFormatter, ConnectionsAgentPlayerFormatter

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

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all word groups; \
therefore, you should try your best to minimize the number of guesses.\
"""

CONNECTIONS_GUESS_FORMAT = """\
Your guess should be the **indices of the guessed words**, NOT the words themselves.\
"""


class ConnectionsAgentMemory(
    BaseAgentMemory[
        ConnectionsInfo,
        None,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
    ],
    ConnectionsAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, note_cls=ConnectionsNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_GAME_RULE
        yield CONNECTIONS_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word group laws and possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you successfully found a group."

    @override
    def get_note_example(self) -> ConnectionsNote:
        return ConnectionsNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ConnectionsAgentPlayer(
    BaseAgentPlayer[ConnectionsInfo, None, ConnectionsGuess, ConnectionsFeedback, ConnectionsNote],
    ConnectionsAgentPlayerFormatter,
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str], None],
        agent_log_func: Callable[[str], None],
    ) -> None:
        super().__init__(
            memory=ConnectionsAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=ConnectionsGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONNECTIONS_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield CONNECTIONS_GUESS_FORMAT
        example: range = range(self.memory.game_info.group_size)

        yield (
            f"For example, reply {', '.join(map(str, example))} if you choose "
            f"{', '.join(self.memory.game_info.words[index] for index in example)}."
        )

    @override
    def get_guess_example(self, *, hint: None) -> ConnectionsGuess:
        return ConnectionsGuess(indices=list(range(self.memory.game_info.group_size)))
