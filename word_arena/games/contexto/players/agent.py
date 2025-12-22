from collections.abc import Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import ContextoExperience, ContextoFeedback, ContextoFinalResult, ContextoGuess
from ..formatters.agent import ContextoAgentMemoryFormatter, ContextoAgentPlayerFormatter

CONTEXTO_ROLE_DEF = "You are an intelligent AI good at understanding word relations."

CONTEXTO_GAME_RULE = """You are playing a game where you need to find a secret word.

The game holds a word list with tens of thousands words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, you choose a word as your next guess; the word will be lemmatized to its stem form.

If the word is accepted, you will see its lemma and the lemma's position in the list,
otherwise you will see the reject reason, such as invalid format, word not in list, or taboo words.

You should try your best to minimize the number of guesses; there may be a guessing limit."""

CONTEXTO_GUESS_FORMAT = (
    "Your guess must be a **single word with only lowercase letters and no hyphens**."
)


class ContextoAgentMemory(
    BaseAgentMemory[
        int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoExperience
    ],
    ContextoAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the word similarity laws and possible strategies"

    def __init__(self, *, model: BaseLLM):
        super().__init__(model=model, experience_cls=ContextoExperience)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_GAME_RULE
        yield CONTEXTO_GUESS_FORMAT

    @override
    def make_create_experience_prompt(self) -> Iterator[str]:
        yield f"Now, initialize some {self.NOTE_PROMPT}."

    @override
    def make_update_experience_prompt(self) -> Iterator[str]:
        yield f"Now, create an updated version of your {self.NOTE_PROMPT}."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you guessed very close or very far words."

    @override
    def get_experience_example(self) -> ContextoExperience:
        return ContextoExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ContextoAgentPlayer(
    BaseAgentPlayer[int, None, ContextoGuess, ContextoFeedback, ContextoExperience],
    ContextoAgentPlayerFormatter,
):
    def __init__(self, *, model: BaseLLM, prompt_mode: PromptMode):
        super().__init__(
            memory=ContextoAgentMemory(model=model),
            model=model,
            prompt_mode=prompt_mode,
            guess_cls=ContextoGuess,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_GAME_RULE

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
            yield "Write a paragraph to update your knowledge about the secret word."

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
        yield CONTEXTO_GUESS_FORMAT
        yield "Pay attention to the number of remaining guesses."

    @override
    def get_guess_example(self, *, hint: None) -> ContextoGuess:
        return ContextoGuess(word="word")
