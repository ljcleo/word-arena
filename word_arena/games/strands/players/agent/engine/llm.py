from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel, Field

from ......players.agent.common import GameRecord
from ......players.agent.engine.llm import BaseLLMAgentEngine
from ......players.agent.state import AgentGameStateInterface, AgentNoteStateInterface
from ....common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo


class StrandsNote(BaseModel):
    strategy: str = Field(title="Possible Strategies")


type StrandsGameStateInterface = AgentGameStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult
]

type StrandsNoteStateInterface = AgentNoteStateInterface[
    StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote
]

type StrandsGameRecord = GameRecord[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult]

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
therefore, you should try your best to minimize the number of guesses.

Your guess should be the **list of coordinates of the guessed path**, NOT the word itself.\
"""


class StrandsLLMAgentEngine(
    BaseLLMAgentEngine[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote]
):
    @property
    @override
    def guess_cls(self) -> type[StrandsGuess]:
        return StrandsGuess

    @property
    @override
    def note_cls(self) -> type[StrandsNote]:
        return StrandsNote

    @override
    def make_role_def_prompt(self) -> Iterator[str]:
        yield STRANDS_ROLE_DEF

    @override
    def make_game_rule_prompt(self) -> Iterator[str]:
        yield STRANDS_GAME_RULE

    @override
    def make_note_detail_prompt(self) -> Iterator[str]:
        yield "Your notes should cover possible strategies."

    @override
    def make_guess_detail_prompt(self, *, game_state: StrandsGameStateInterface) -> Iterator[str]:
        yield "Pay attention to the number of remaining guesses."

    @override
    def make_reflect_detail_prompt(self) -> Iterator[str]:
        yield "Pay attention to the rounds where you successfully found a theme word or spangram."

    @override
    def get_note_example(self) -> StrandsNote:
        return StrandsNote(strategy="Follow these strategies when guessing: ...")

    @override
    def get_guess_example(self, *, game_state: StrandsGameStateInterface) -> StrandsGuess:
        return StrandsGuess(coords=[(0, 0), (0, 1), (1, 2), (1, 1), (0, 2)])

    @override
    def prompt_game_info(
        self, *, game_state: StrandsGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_state.game_info)

    @override
    def prompt_guess(
        self, *, game_state: StrandsGameStateInterface, guess: StrandsGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_state.game_info, guess=guess)

    @override
    def prompt_feedback(
        self,
        *,
        game_state: StrandsGameStateInterface,
        guess: StrandsGuess,
        feedback: StrandsFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_game_info_final(
        self, *, game_record: StrandsGameRecord
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_game_info(game_info=game_record.trajectory.game_info)

    @override
    def prompt_guess_final(
        self, *, game_record: StrandsGameRecord, turn_index: int, guess: StrandsGuess
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_guess(game_info=game_record.trajectory.game_info, guess=guess)

    @override
    def prompt_feedback_final(
        self,
        *,
        game_record: StrandsGameRecord,
        turn_index: int,
        guess: StrandsGuess,
        feedback: StrandsFeedback,
    ) -> Iterator[tuple[str, str]]:
        yield from self._prompt_feedback(feedback=feedback)

    @override
    def prompt_final_result(self, *, game_record: StrandsGameRecord) -> Iterator[tuple[str, str]]:
        final_result: StrandsFinalResult = game_record.final_result

        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        spangram_str: str = self._format_words(infos=final_result.answers[:1])
        spangram_found: bool = 0 in final_result.found_indices

        found_theme_indices: list[int] = [
            index for index in final_result.found_indices if index != 0
        ]

        missed_theme_indices: list[int] = [
            index
            for index in range(1, len(final_result.answers))
            if index not in found_theme_indices
        ]

        if spangram_found:
            yield "Found Spangram", spangram_str

        if len(found_theme_indices) > 0:
            yield (
                "Found Theme Words",
                self._format_words(
                    infos=map(final_result.answers.__getitem__, found_theme_indices)
                ),
            )

        if not spangram_found:
            yield "Spangram Not Found", spangram_str

        if len(missed_theme_indices) > 0:
            yield (
                "Theme Words Not Found",
                self._format_words(
                    infos=map(final_result.answers.__getitem__, missed_theme_indices)
                ),
            )

    def _prompt_game_info(self, *, game_info: StrandsInfo) -> Iterator[tuple[str, str]]:
        yield "Board", "\n".join(game_info.board)
        yield "Clue", game_info.clue

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    def _prompt_guess(
        self, *, game_info: StrandsInfo, guess: StrandsGuess
    ) -> Iterator[tuple[str, str]]:
        word: str = "(N/A)"
        buffer: list[str] = []
        visited: set[tuple[int, int]] = set()

        for i in range(len(guess.coords)):
            cx: int
            cy: int
            cx, cy = guess.coords[i]

            if not (0 <= cx < 8 and 0 <= cy < 6 and (cx, cy) not in visited):
                break

            buffer.append(game_info.board[cx][cy])
            visited.add((cx, cy))

            if i < len(guess.coords) - 1:
                dx: int = guess.coords[i + 1][0] - cx
                dy: int = guess.coords[i + 1][1] - cy

                if not ((dx != 0 or dy != 0) and -1 <= dx <= 1 and -1 <= dy <= 1):
                    break
        else:
            word = "".join(buffer)

        coords_str: str = " -> ".join(f"({x}, {y})" for x, y in guess.coords)
        yield "Guessed Word", f"{word} [{coords_str}]"

    def _prompt_feedback(self, *, feedback: StrandsFeedback) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, int):
            yield "Validation Result", "Accept"
            yield "Guess Result", ("Missed", "Theme Word", "Spangram")[feedback]
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback

    def _format_words(self, *, infos: Iterable[tuple[str, list[tuple[int, int]]]]) -> str:
        return "; ".join(self._format_word(word=word, coords=coords) for word, coords in infos)

    def _format_word(self, *, word: str, coords: list[tuple[int, int]]) -> str:
        coords_str: str = " -> ".join(f"({x}, {y})" for x, y in coords)
        return f"{word} [{coords_str}]"
