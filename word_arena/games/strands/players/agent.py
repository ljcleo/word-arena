from collections.abc import Callable, Iterator
from typing import override

from ....common.llm.base import BaseLLM
from ....common.player.agent.memory import BaseAgentMemory
from ....common.player.agent.player import BaseAgentPlayer
from ..common import (
    StrandsFeedback,
    StrandsFinalResult,
    StrandsGuess,
    StrandsInfo,
    StrandsNote,
)
from ..formatters.agent import StrandsAgentMemoryFormatter, StrandsAgentPlayerFormatter

STRANDS_ROLE_DEF = """\
You are an intelligent AI with a good English vocabulary.

You are playing a game where you need to find secret words arranged in a grid.
"""

STRANDS_GAME_RULE = """\
The game holds a spangram and several theme words, and gives a clue about them; \
a spangram can have one or more words, while each theme word is strictly one word.

The secret spangram and theme words are arranged into a 8x6 grid, \
where each cell is a letter that only belongs to one theme word or the spangram; \
the coordinates are in the form of `(row, column)`, \
where rows are from 0 to 7 and columns are from 0 to 5.

Each theme word and the spangram can be found continuous and non-overlapping in the grid: \
you can draw a path on the grid that reads exactly the theme word or spangram, \
where adjacent vertices are 8-connected and no cells are visited twice; \
furthermore, paths of all theme words and the spangram do not use common cells, \
and pass all cells in the grid exactly once.

The spangram describes the game's theme; it always touches two opposite sides of the board, \
either from row 0 to row 7 or from column 0 to column 5, or both.

Every time, you draw a path on the grid to form a guess; \
the path must be continuous and non-overlapping, \
and must not use cells that belong to the theme words or spangram that you have found.

If the path is valid, you will see whether it hits a theme word or the spangram or misses; \
a miss can either mean selecting the wrong word or selecting the right word at the wrong location.

If the path is invalid, it will be rejected and you will see the reason.

There may be a guessing limit on the total number of guesses (including rejected ones), and \
the game halts if the remaining guesses are not enough to find all theme words and the spangram; \
therefore, you should try your best to minimize the number of guesses.\
"""

STRANDS_GUESS_FORMAT = """\
Your guess should be the **list of coordinates of the guessed path**, NOT the word itself.\
"""


class StrandsAgentMemory(
    BaseAgentMemory[
        StrandsInfo,
        None,
        StrandsGuess,
        StrandsFeedback,
        StrandsFinalResult,
        StrandsNote,
    ],
    StrandsAgentMemoryFormatter,
):
    def __init__(self, *, model: BaseLLM, log_func: Callable[[str], None]) -> None:
        super().__init__(model=model, note_cls=StrandsNote, log_func=log_func)

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield STRANDS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield STRANDS_GAME_RULE
        yield STRANDS_GUESS_FORMAT

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you successfully found a theme word or spangram."

    @override
    def get_note_example(self) -> StrandsNote:
        return StrandsNote(strategy="Follow these strategies when guessing: ...")


class StrandsAgentPlayer(
    BaseAgentPlayer[StrandsInfo, None, StrandsGuess, StrandsFeedback, StrandsNote],
    StrandsAgentPlayerFormatter,
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
            memory=StrandsAgentMemory(model=model, log_func=agent_log_func),
            model=model,
            do_analyze=do_analyze,
            guess_cls=StrandsGuess,
            player_log_func=player_log_func,
            agent_log_func=agent_log_func,
        )

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield STRANDS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield STRANDS_GAME_RULE

    @override
    def make_guess_detail_prompt(self, *, hint: None) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."
        yield STRANDS_GUESS_FORMAT

    @override
    def get_guess_example(self, *, hint: None) -> StrandsGuess:
        return StrandsGuess(coords=[(0, 0), (0, 1), (1, 2), (1, 1), (0, 2)])
