from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import ContextoFeedback, ContextoFinalResult, ContextoGuess, ContextoNote
from ..formatters.agent import ContextoAgentMemoryFormatter, ContextoAgentPlayerFormatter

CONTEXTO_ROLE_DEF = """\
You are an intelligent AI good at understanding word relations.

You are playing a game where you need to find a secret word.\
"""

CONTEXTO_GAME_RULE = """\
The game holds a word list with tens of thousands words, including the secret word, \
sorted by the similarity to the secret word.

The position of the secret word is 1; the position of the word closest to the secret word \
(but not the secret word itself) is 2; the position of the furthest word is 500.

Word similarity is based on the context in which words are used on the internet, \
related to both meaning and proximity.

Every time, you choose a word as your next guess; the word will be lemmatized to its stem form.

If the word is accepted, you will see its lemma and the lemma's position in the list, \
otherwise you will see the reject reason, such as invalid format, word not in list, or taboo words.

You should try your best to minimize the number of guesses; there may be a guessing limit.\
"""

CONTEXTO_GUESS_FORMAT = """\
Your guess should be a **single word with only lowercase letters and no hyphens**.\
"""


class ContextoAgentMemory(
    BaseAgentMemory[int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote],
    ContextoAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, note_cls=ContextoNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_GAME_RULE
        yield CONTEXTO_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover empirical word similarity laws and possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you guessed very close or very far words."

    @override
    def get_note_example(self) -> ContextoNote:
        return ContextoNote(
            law="...", strategy="Follow these rules and strategies when guessing: ..."
        )


class ContextoAgentPlayer(
    BaseAgentPlayer[int, None, ContextoGuess, ContextoFeedback, ContextoNote],
    ContextoAgentPlayerFormatter,
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
            memory=ContextoAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=ContextoGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield CONTEXTO_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield CONTEXTO_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield CONTEXTO_GUESS_FORMAT

    @override
    def get_guess_example(self, *, hint: None) -> ContextoGuess:
        return ContextoGuess(word="word")
