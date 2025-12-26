from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo, WordleNote
from ..formatters.agent import WordleAgentMemoryFormatter, WordleAgentPlayerFormatter

WORDLE_ROLE_DEF = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find one or more secret words.\
"""

WORDLE_GAME_RULE = """\
All secret words have 5 letters, and are selected from a large vocabulary that \
covers most of the 5-letter English words.

Every time, you choose a 5-letter word as your next guess; the guess should be a valid English word.

If the word is accepted, you will see how it matches each secret word through a labeling string:

A `G` label means that the letter at that position is correct; \
a `Y` label means that the letter at that position should be at somewhere else; \
a `.` means that the letter is not in the secret word, or has appeared too many times.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn, \
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones), \
and the game halts if the remaining guesses are not enough to find all secret words; \
therefore, you should try your best to minimize the number of guesses.\
"""

WORDLE_GUESS_FORMAT = """\
Your guess must be a **single word with 5 lowercase letters**.\
"""


class WordleAgentMemory(
    BaseAgentMemory[WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote],
    WordleAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, note_cls=WordleNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE
        yield WORDLE_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> WordleNote:
        return WordleNote(strategy="Follow these rules and strategies when guessing: ...")


class WordleAgentPlayer(
    BaseAgentPlayer[WordleInfo, None, WordleGuess, WordleFeedback, WordleNote],
    WordleAgentPlayerFormatter,
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
            memory=WordleAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=WordleGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield WORDLE_GUESS_FORMAT

    @override
    def get_guess_example(self, *, hint: None) -> WordleGuess:
        return WordleGuess(word="word")
