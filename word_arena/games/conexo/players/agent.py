from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import ConexoExperience, ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ..formatters.agent import ConexoAgentMemoryFormatter, ConexoAgentPlayerFormatter

CONEXO_ROLE_DEF = "You are an intelligent AI good at understanding word relations."

CONEXO_GAME_RULE: str = """You are playing a game where you need to find the groups behind words.

The game holds several word groups of the same size;
each group has a common theme that shall cover all words in the group,
which can be lexical, semantic, conceptual, phrasal (can form phrases with the same word),
or any general co-membership (e.g., work titles by the same artist).

At the beginning, the game provides the group size and words from all groups (indexed from 0),
but not the groups themselves; it is guaranteed that each word belongs to exactly one group.

Every time, you choose as many words as the group size to form a guess,
then you will see whether the guessed words belong to the same group or not;
if yes, then the group is considered found.

If you guess an incorrect number of words, or guess words that already belong to a found group,
then the guess will be rejected.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all word groups;
therefore, you should try your best to minimize the number of guesses."""

CONEXO_GUESS_FORMAT = "You should reply the indices of the guessed words, NOT the words themselves."


class ConexoAgentMemory(
    BaseAgentMemory[
        ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoExperience
    ],
    ConexoAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the word group laws and possible strategies"

    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, experience_cls=ConexoExperience, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONEXO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONEXO_GAME_RULE
        yield CONEXO_GUESS_FORMAT

    @override
    def make_create_experience_prompt(self) -> Iterator[str]:
        yield f"Now, initialize some {self.NOTE_PROMPT}."

    @override
    def make_update_experience_prompt(self) -> Iterator[str]:
        yield f"Now, create an updated version of your {self.NOTE_PROMPT}."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you successfully found a group."

    @override
    def get_experience_example(self) -> ConexoExperience:
        return ConexoExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ConexoAgentPlayer(
    BaseAgentPlayer[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoExperience],
    ConexoAgentPlayerFormatter,
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
            memory=ConexoAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=ConexoGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONEXO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONEXO_GAME_RULE

    @override
    def make_full_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield (
                "Understand the game rules and analyze the given words, "
                "then plan and make your next guess."
            )
        else:
            yield (
                "Analyze the situation based on your previous analysis and the latest feedback, "
                "then plan and make your next guess."
            )

    @override
    def make_simple_guess_prompt(self) -> Iterator[str]:
        yield "Make your next guess."

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield CONEXO_GUESS_FORMAT
        example: range = range(self.memory.game_info.group_size)

        yield (
            f"For example, reply {', '.join(map(str, example))} if you choose "
            f"{', '.join(self.memory.game_info.words[index] for index in example)}."
        )

        yield "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(self, *, hint: None) -> ConexoGuess:
        return ConexoGuess(indices=list(range(self.memory.game_info.group_size)))
