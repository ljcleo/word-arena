from collections.abc import Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import WordleExperience, WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ..formatters.agent import WordleAgentMemoryFormatter, WordleAgentPlayerFormatter

WORDLE_ROLE_DEF = "You are an intelligent AI with a good English vocabulary."

WORDLE_GAME_RULE = """You are playing a game where you need to find one or more secret words.

All secret words have 5 letters, and are selected from a large vocabulary that
covers most of the 5-letter English words.

Every time, you choose a 5-letter word as your next guess; the guess should be a valid English word.

If the word is accepted, you will see how it matches each secret word through a labeling string:

A `G` label means that the letter at that position is correct;
a `Y` label means that the letter at that position should be at somewhere else;
a `.` means that the letter is not in the secret word, or has appeared too many times.

If the word is rejected, you will see the reason, such as invalid format or word not in vocabulary.

A secret word is considered found if and only if the word is actually guessed in a turn,
so you will need at least as many guesses as there are secret words to find all of them.

There may be a guessing limit on the total number of guesses (including rejected ones),
and the game halts if the remaining guesses are not enough to find all secret words;
therefore, you should try your best to minimize the number of guesses."""

WORDLE_GUESS_FORMAT = "Your guess must be a **single word with 5 lowercase letters**."


class WordleAgentMemory(
    BaseAgentMemory[
        WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult, WordleExperience
    ],
    WordleAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the possible strategies"

    def __init__(self, *, model: BaseLLM):
        super().__init__(model=model, experience_cls=WordleExperience)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE
        yield WORDLE_GUESS_FORMAT

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
    def get_experience_example(self) -> WordleExperience:
        return WordleExperience(strategy="Follow these rules and strategies when guessing: ...")


class WordleAgentPlayer(
    BaseAgentPlayer[WordleInfo, None, WordleGuess, WordleFeedback, WordleExperience],
    WordleAgentPlayerFormatter,
):
    def __init__(self, *, model: BaseLLM, do_analyze: bool):
        super().__init__(
            memory=WordleAgentMemory(model=model),
            model=model,
            do_analyze=do_analyze,
            guess_cls=WordleGuess,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE

    @override
    def make_full_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, then plan and make your first guess."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the secret word, then plan and make your next guess."
            )

    @override
    def make_simple_guess_prompt(self) -> Iterator[str]:
        yield f"Make your {'first' if self.memory.num_guesses == 0 else 'next'} guess."

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield WORDLE_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(self, *, hint: None) -> WordleGuess:
        return WordleGuess(word="word")
