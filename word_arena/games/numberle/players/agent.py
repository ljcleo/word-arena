from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import (
    NumberleExperience,
    NumberleFeedback,
    NumberleFinalResult,
    NumberleGuess,
    NumberleInfo,
)
from ..formatters.agent import NumberleAgentMemoryFormatter, NumberleAgentPlayerFormatter

Numberle_ROLE_DEF = "You are an intelligent AI good at basic arithmetics."

Numberle_GAME_RULE = """You are playing a game where you need to find one or more secret equations.

All secret equations have the same number of characters, with both hand sides
basic arithmetic expressions containing digits and `+-*/` only, connected by a single `=`;
brackets, negative numbers, decimals, leading zeros, and zero divisions are NOT allowed.

Every time, you choose an equation as your next guess; the guess should be a valid equation
following the same length and format constraints described above, **without any whitespaces**.

If the equation is accepted, you will see how it matches each secret equation
through a labeling string:

A `G` label means that the character at that position is correct;
a `Y` label means that the character at that position should be at somewhere else;
a `.` means that the character is not in the secret equation, or has appeared too many times.

If the equation is rejected, you will see the reason, which shall be invalid format.

A secret equation is considered found if and only if the equation is actually guessed in a turn,
so you will need at least as many guesses as there are secret equations to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all secret equations;
therefore, you should try your best to minimize the number of guesses."""

Numberle_GUESS_FORMAT = (
    "Your guess must be a "
    "**single equation obeying the length and format constraints without any whitespaces**."
)


class NumberleAgentMemory(
    BaseAgentMemory[
        NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleExperience
    ],
    NumberleAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the possible strategies"

    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, experience_cls=NumberleExperience, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield Numberle_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield Numberle_GAME_RULE
        yield Numberle_GUESS_FORMAT

    @override
    def make_create_experience_prompt(self) -> Iterator[str]:
        yield f"Now, initialize some {self.NOTE_PROMPT}."

    @override
    def make_update_experience_prompt(self) -> Iterator[str]:
        yield f"Now, create an updated version of your {self.NOTE_PROMPT}."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_experience_example(self) -> NumberleExperience:
        return NumberleExperience(strategy="Follow these rules and strategies when guessing: ...")


class NumberleAgentPlayer(
    BaseAgentPlayer[NumberleInfo, None, NumberleGuess, NumberleFeedback, NumberleExperience],
    NumberleAgentPlayerFormatter,
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
            memory=NumberleAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=NumberleGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield Numberle_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield Numberle_GAME_RULE

    @override
    def make_full_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, then plan and make your first guess."
        else:
            yield (
                "Analyze the situation based on your previous analysis and the latest feedback, "
                "then plan and make your next guess."
            )

    @override
    def make_simple_guess_prompt(self) -> Iterator[str]:
        yield f"Make your {'first' if self.memory.num_guesses == 0 else 'next'} guess."

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield Numberle_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(self, *, hint: None) -> NumberleGuess:
        return NumberleGuess(equation="5-4*3/2+1=0")
