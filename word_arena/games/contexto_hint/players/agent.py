from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import ContextoHintGuess, ContextoHintNote
from ..formatters.agent import ContextoHintAgentMemoryFormatter, ContextoHintAgentPlayerFormatter

CONTEXTO_HINT_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.\
"""

CONTEXTO_HINT_GAME_RULE = """\
The game holds a word list with 500 words, including the secret word, \
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word \
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet, \
related to both meaning and proximity.

Every time, the game provides several candidate words (indexed from 0) from the list that \
you have not guessed before, but without their positions.

You need to choose one of them as your next guess, then you will see its position in the list.

It is guaranteed that there is a candidate word closer than the current best guess.\
"""

CONTEXTO_HINT_GUESS_FORMAT = """\
Your guess should be the **index of the guessed word**, NOT the word itself.\
"""


class ContextoHintAgentMemory(
    BaseAgentMemory[None, list[str], ContextoHintGuess, int, list[str], ContextoHintNote],
    ContextoHintAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str, str], None]) -> None:
        super().__init__(model=model, note_cls=ContextoHintNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_GAME_RULE
        yield CONTEXTO_HINT_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word similarity laws and possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield (
            "Pay attention to the rounds where you failed to choose the word "
            "with the closest position among the candidates."
        )

    @override
    def get_note_example(self) -> ContextoHintNote:
        return ContextoHintNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ContextoHintAgentPlayer(
    BaseAgentPlayer[None, list[str], ContextoHintGuess, int, ContextoHintNote],
    ContextoHintAgentPlayerFormatter,
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
            memory=ContextoHintAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=ContextoHintGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_HINT_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: list[str]) -> Iterator[str]:
        yield CONTEXTO_HINT_GUESS_FORMAT
        example: int = len(hint) - 1
        yield f"For example, reply {example} if you choose {hint[example]}."

    @override
    def get_guess_example(self, *, hint: list[str]) -> ContextoHintGuess:
        return ContextoHintGuess(index=len(hint) - 1)
