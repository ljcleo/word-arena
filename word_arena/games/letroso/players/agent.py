from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo, LetrosoNote
from ..formatters.agent import LetrosoAgentMemoryFormatter, LetrosoAgentPlayerFormatter

LETROSO_ROLE_DEF = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

LETROSO_GAME_RULE = """\
All secret words are selected from a large vocabulary that covers most of the English words, \
yet their lengths may vary.

Every time, you choose a word as your next guess; \
the guess should be a valid English word with no more than a specific number of letters.

If the word is accepted, you will see how it matches each secret word \
through a bracketed labeling string the same length as the guessed word:

A `G` label or `>` label means that the relative order of the letter at that position, \
compared to other `G`-labeled or `>`-labeled letters, is the same in the secret word; \
however, its absolute position in the secret word can be different.

A `Y` label means that the letter at that position appears in the secret word, \
but its relative order, compared to `G`-labeled or `>`-labeled letters, is incorrect; \
a `.` label means that the letter is not in the secret word, or appears too many times.

Furthermore, `>` always appears right after `G` or `>`, forming a `G`-sequence like `G>>>`, \
meaning that the corresponding letters appear together in the secret word, adjacent to each other.

Directly adjacent `G`-sequences are NOT adjacent to each other in the secret word: \
for example, `GG` (NOT `G>`) means that the two adjacent letters in the guessed word \
are NOT adjacent in the secret word, though the relative order is correct; \
however, this does not apply to non-directly adjacent `G`-sequences like in `GYG`.

The default brackets are `[` and `]`, \
and `(` at the beginning means that the secret word starts with the first `G`-sequence, \
while `)` at the end means that the secret word ends with the last `G`-sequence; \
therefore, the secret word itself will be labeled like `(G>>>>)`.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn, \
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all secret words; \
therefore, you should try your best to minimize the number of guesses.\
"""

LETROSO_GUESS_FORMAT = """\
Your guess should be a **single word with only lowercase letters within the length constraint**.\
"""


class LetrosoAgentMemory(
    BaseAgentMemory[
        LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote
    ],
    LetrosoAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str, str], None]) -> None:
        super().__init__(model=model, note_cls=LetrosoNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield LETROSO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield LETROSO_GAME_RULE
        yield LETROSO_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> LetrosoNote:
        return LetrosoNote(strategy="Follow these strategies when guessing: ...")


class LetrosoAgentPlayer(
    BaseAgentPlayer[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoNote],
    LetrosoAgentPlayerFormatter,
):
    def __init__(
        self,
        *,
        model: BaseLLM,
        do_analyze: bool,
        player_log_func: Callable[[str, str], None],
        agent_log_func: Callable[[str, str], None],
    ) -> None:
        super().__init__(
            memory=LetrosoAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=LetrosoGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield LETROSO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield LETROSO_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield LETROSO_GUESS_FORMAT

    @override
    def get_guess_example(self, *, hint: None) -> LetrosoGuess:
        return LetrosoGuess(word="word")
