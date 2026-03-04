from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import (
    TuringFeedback,
    TuringFinalResult,
    TuringGuess,
    TuringInfo,
    TuringNote,
)
from ..formatters.agent import TuringAgentMemoryFormatter, TuringAgentPlayerFormatter

TURING_ROLE_DEF = """\
You are an intelligent AI good at logic deduction.

You are playing a game where you need to find a secret code with digits.\
"""

TURING_GAME_RULE = """\
The game holds a 3-digit secret code `xyz`, where each digit `x`, `y` and `z` ranges from 1 to 5.

Multiple verifiers (indexed from 0) are available to help you find out the secret code, \
each of which holds a boolean criterion concerning `x`, `y` and `z` \
(e.g. `x < y` or `x + y + z > 6`), and tells whether an input code satisfies that criterion.

Each verifier will show at least two candidate criteria at the beginning of the game, \
but will only use one of them for verification throughout the game, \
so you will need to figure out which criterion the verifier actually verifies.

It is satisfied that ONLY the secret code passes all verifiers, \
and all other codes will fail on some verifier(s);
furthermore, it is guaranteed that no verifier is superfluous.

Your guesses will consist of multiple verifying guesses and one last final guess.

In a verifying guess, you propose a 3-digit code, each digit ranging from 1 to 5, \
along with 1 to 3 verifier indices to which you want to input the code; \
the chosen verifiers will return yes or no according to your code and their hidden criterion.

When you believe you have figured out the secret code, you can make your final guess, \
where you propose the secret code along with an empty verifier list; \
the game then ends immediately, returning whether you have successfully find the secret code or not.

If your guess (both verifying and final) does not follow the above format, \
then the guess will be rejected, and you will see why. \

There may be a guessing limit on the total number of guesses \
(including verifying, final and rejected ones); \
therefore, you should try your best to minimize the number of guesses.\
"""

TURING_GUESS_FORMAT = """\
Your guess should be a **3-digit code plus a list of verifier indices \
(empty for the final guess)**.\
"""


class TuringAgentMemory(
    BaseAgentMemory[TuringInfo, None, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote],
    TuringAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, note_cls=TuringNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield TURING_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield TURING_GAME_RULE
        yield TURING_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_note_example(self) -> TuringNote:
        return TuringNote(strategy="Follow these strategies when guessing: ...")


class TuringAgentPlayer(
    BaseAgentPlayer[TuringInfo, None, TuringGuess, TuringFeedback, TuringNote],
    TuringAgentPlayerFormatter,
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
            memory=TuringAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=TuringGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield TURING_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield TURING_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield TURING_GUESS_FORMAT

    @override
    def get_guess_example(self, *, hint: None) -> TuringGuess:
        return TuringGuess(code=123, verifiers=[0, 1, 2])
