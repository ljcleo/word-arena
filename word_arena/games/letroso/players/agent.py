from collections.abc import Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import (
    LetrosoExperience,
    LetrosoFeedback,
    LetrosoFinalResult,
    LetrosoGuess,
    LetrosoInfo,
)
from ..formatters.agent import LetrosoAgentMemoryFormatter, LetrosoAgentPlayerFormatter

LETROSO_ROLE_DEF = "You are an intelligent AI with a good English vocabulary."

LETROSO_GAME_RULE = """You are playing a game where you need to find one or more secret words.

All secret words are selected from a large vocabulary that covers most of the English words,
yet their lengths may vary.

Every time, you choose a word as your next guess;
the guess should be a valid English word with no more than a specific number of letters.

If the word is accepted, you will see how it matches each secret word
through a labeling string the same length as the guessed word:

A `G` label means that the relative order of the letter at that position,
compared to other `G`-labeled letters, is the same in the secret word;
however, its absolute position in the secret word can be different.

A `Y` label means that the letter at that position appears in the secret word,
but its relative order compared to `G`-labeled letters is incorrect;
a `.` label means that the letter is not in the secret word, or has appeared too many times.

Furthermore, if multiple labels are braced in `[]` (e.g., `[GGG]`), they form a segment,
and the corresponding letters appears together in the secret word, adjacent to each other;
letters from different segments are NOT adjacent to each other in the secret word,
even if the segments themselves are adjacent (e.g., `[G][G]`).

A head segment started by `(` instead of `[` means that the secret word starts with it,
while a `[` start means that the secret word does NOT start with this segment;
a tail segment ended by `)` instead of `]` means that the secret word ends with it,
while a `]` end means that the secret word does NOT end with this segment.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn,
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all secret words;
therefore, you should try your best to minimize the number of guesses."""

LETROSO_GUESS_FORMAT = (
    "Your guess should be a "
    "**single word with only lowercase letters no more than the length constraint**."
)


class LetrosoAgentMemory(
    BaseAgentMemory[
        LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience
    ],
    LetrosoAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the possible strategies"

    def __init__(self, *, model: BaseLLM):
        super().__init__(model=model, experience_cls=LetrosoExperience)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield LETROSO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield LETROSO_GAME_RULE
        yield LETROSO_GUESS_FORMAT

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
    def get_experience_example(self) -> LetrosoExperience:
        return LetrosoExperience(strategy="Follow these rules and strategies when guessing: ...")


class LetrosoAgentPlayer(
    BaseAgentPlayer[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoExperience],
    LetrosoAgentPlayerFormatter,
):
    def __init__(self, *, model: BaseLLM, prompt_mode: PromptMode):
        super().__init__(
            memory=LetrosoAgentMemory(model=model),
            model=model,
            prompt_mode=prompt_mode,
            guess_cls=LetrosoGuess,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield LETROSO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield LETROSO_GAME_RULE

    @override
    def make_full_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, then plan and make your first guess."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the secret words, then plan and make your next guess."
            )

    @override
    def make_summarize_analysis_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to summarize your past analysis and plans before this turn."

    @override
    def make_analyze_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Write a paragraph to understand the game rules."
        else:
            yield "Write a paragraph to update your knowledge about the secret words."

    @override
    def make_plan_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Write a paragraph to plan the first guess."
        else:
            yield "Write a paragraph to plan the next guess."

    @override
    def make_simple_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Make your first guess."
        else:
            yield "Make your next guess."

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield LETROSO_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(self, *, hint: None) -> LetrosoGuess:
        return LetrosoGuess(word="word")
