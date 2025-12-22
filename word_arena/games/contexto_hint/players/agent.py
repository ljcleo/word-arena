from collections.abc import Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.common import PromptMode
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import ContextoHintExperience, ContextoHintGuess
from ..formatters.agent import ContextoHintAgentMemoryFormatter, ContextoHintAgentPlayerFormatter

CONTEXTO_HINT_ROLE_DEF = "You are an intelligent AI good at understanding word relations."

CONTEXTO_HINT_GAME_RULE: str = """You are playing a game where you need to find a secret word.

The game holds a word list with 500 words, including the secret word,
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet,
related to both meaning and proximity.

Every time, the game provides several candidate words (indexed from 0) from the list that
you have not guessed before, but without their positions.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess."""

CONTEXTO_HINT_GUESS_FORMAT = "You should reply the index of the guessed word, NOT the word itself."


class ContextoHintAgentMemory(
    BaseAgentMemory[None, list[str], ContextoHintGuess, int, list[str], ContextoHintExperience],
    ContextoHintAgentMemoryFormatter,
):
    NOTE_PROMPT: str = "notes about the word similarity laws and possible strategies"

    def __init__(self, *, model: BaseLLM):
        super().__init__(model=model, experience_cls=ContextoHintExperience)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_GAME_RULE
        yield CONTEXTO_HINT_GUESS_FORMAT

    @override
    def make_create_experience_prompt(self) -> Iterator[str]:
        yield f"Now, initialize some {self.NOTE_PROMPT}."

    @override
    def make_update_experience_prompt(self) -> Iterator[str]:
        yield f"Now, create an updated version of your {self.NOTE_PROMPT}."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield (
            "Pay attention to the rounds where you failed to choose the word "
            "with the closest position among the candidates."
        )

    @override
    def get_experience_example(self) -> ContextoHintExperience:
        return ContextoHintExperience(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ContextoHintAgentPlayer(
    BaseAgentPlayer[None, list[str], ContextoHintGuess, int, ContextoHintExperience],
    ContextoHintAgentPlayerFormatter,
):
    def __init__(self, *, model: BaseLLM, prompt_mode: PromptMode):
        super().__init__(
            memory=ContextoHintAgentMemory(model=model),
            model=model,
            prompt_mode=prompt_mode,
            guess_cls=ContextoHintGuess,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_GAME_RULE

    @override
    def make_full_guess_prompt(self) -> Iterator[str]:
        if self.memory.num_guesses == 0:
            yield "Understand the game rules, plan for your next guess and make your choice."
        else:
            yield (
                "Summarize your past analysis and plans before this turn, "
                "update your knowledge about the secret word, "
                "plan your next guess and make your choice."
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
        yield "Write a paragraph to plan your next guess."

    @override
    def make_simple_guess_prompt(self) -> Iterator[str]:
        yield "Make your choice."

    @override
    def make_guess_detail_prompt(self, *, hint: list[str]) -> Iterator[str]:
        yield CONTEXTO_HINT_GUESS_FORMAT
        example: int = len(hint) - 1
        yield f"For example, reply {example} if you choose {hint[example]}."

    @override
    def get_guess_example(self, *, hint: list[str]) -> ContextoHintGuess:
        return ContextoHintGuess(index=len(hint) - 1)
