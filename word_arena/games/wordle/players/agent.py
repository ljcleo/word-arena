from collections.abc import Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import WordleExperience, WordleFeedback, WordleFinalResult, WordleInfo
from ..formatter import WordleAgentFormatter
from .log import WordleLogPlayer

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
    BaseAgentMemory[WordleInfo, None, str, WordleFeedback, WordleFinalResult, WordleExperience]
):
    def __init__(self, *, model: BaseLLM):
        super().__init__(
            model=model,
            experience_cls=WordleExperience,
            agent_formatter_cls=WordleAgentFormatter,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield WORDLE_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield WORDLE_GAME_RULE
        yield WORDLE_GUESS_FORMAT

    @override
    def make_create_experience_prompt(self) -> Iterator[str]:
        yield "Now, initialize some notes about the possible strategies."

    @override
    def make_update_experience_prompt(self) -> Iterator[str]:
        yield "Now, update your notes about the possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you had little information gain."

    @override
    def get_experience_example(self) -> WordleExperience:
        return WordleExperience(strategy="Follow these rules and strategies when guessing: ...")


class WordleAgentPlayer(
    BaseAgentPlayer[WordleInfo, None, str, WordleFeedback, WordleFinalResult, WordleExperience],
    WordleLogPlayer,
):
    def __init__(self, *, model: BaseLLM, prompt_mode: PromptMode):
        super().__init__(
            memory=WordleAgentMemory(model=model),
            model=model,
            prompt_mode=prompt_mode,
            agent_formatter_cls=WordleAgentFormatter,
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
    def make_summarize_analysis_prompt(self) -> Iterator[str]:
        yield "Write a paragraph to summarize your past analysis and plans before this turn."

    @override
    def make_analyze_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Write a paragraph to understand the game rules."
        else:
            yield "Write a paragraph to update your knowledge about the secret word(s)."

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
        yield WORDLE_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    @override
    def get_raw_guess_example(self, *, hint: None) -> str:
        return "word"
