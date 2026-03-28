from collections.abc import Iterable, Iterator
from typing import override

from pydantic import BaseModel

from .....common.game.common import Trajectory
from .....common.game.renderer.log import BaseLogGameRenderer
from .....utils import join_or_na
from ...common import StrandsError, StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo


class StrandsInfoPromptConfig(BaseModel):
    board: str
    clue: str
    max_turns: str
    unlimited: str


class StrandsFeedbackPromptConfig(BaseModel):
    result: str
    accept: str
    guess_result: str
    guess_verdicts: tuple[str, str, str]
    reject: str
    reject_reason: str
    reject_messages: dict[StrandsError, str]


class StrandsFinalResultPromptConfig(BaseModel):
    result: str
    verdicts: tuple[str, str]
    found_spangram: str
    found_theme_words: str
    missed_spangram: str
    missed_theme_words: str


class StrandsLogPromptConfig(BaseModel):
    game_info: StrandsInfoPromptConfig
    guess: str
    feedback: StrandsFeedbackPromptConfig
    final_result: StrandsFinalResultPromptConfig


class StrandsLogGameRenderer(
    BaseLogGameRenderer[
        StrandsLogPromptConfig, StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult
    ]
):
    @override
    def format_game_info(self, *, game_info: StrandsInfo) -> Iterator[tuple[str, str]]:
        prompt: StrandsInfoPromptConfig = self.prompt_config.game_info
        yield prompt.board, "\n".join(game_info.board)
        yield prompt.clue, game_info.clue

        yield (
            prompt.max_turns,
            prompt.unlimited if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self,
        *,
        trajectory: Trajectory[StrandsInfo, StrandsGuess, StrandsFeedback],
        guess: StrandsGuess,
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

            buffer.append(trajectory.game_info.board[cx][cy])
            visited.add((cx, cy))

            if i < len(guess.coords) - 1:
                dx: int = guess.coords[i + 1][0] - cx
                dy: int = guess.coords[i + 1][1] - cy

                if not ((dx != 0 or dy != 0) and -1 <= dx <= 1 and -1 <= dy <= 1):
                    break
        else:
            word = "".join(buffer)

        yield self.prompt_config.guess, self._format_word(word=word, coords=guess.coords)

    @override
    def format_last_feedback(
        self, *, trajectory: Trajectory[StrandsInfo, StrandsGuess, StrandsFeedback]
    ) -> Iterator[tuple[str, str]]:
        feedback: StrandsFeedback = trajectory.turns[-1].feedback
        prompt: StrandsFeedbackPromptConfig = self.prompt_config.feedback

        if isinstance(feedback, int):
            yield prompt.result, prompt.accept
            yield prompt.guess_result, prompt.guess_verdicts[feedback]
        else:
            yield prompt.result, prompt.reject
            yield prompt.reject_reason, prompt.reject_messages[feedback]

    @override
    def format_final_result(
        self,
        *,
        trajectory: Trajectory[StrandsInfo, StrandsGuess, StrandsFeedback],
        final_result: StrandsFinalResult,
    ) -> Iterator[tuple[str, str]]:
        prompt: StrandsFinalResultPromptConfig = self.prompt_config.final_result

        yield (
            prompt.result,
            prompt.verdicts[len(final_result.found_indices) == len(final_result.answers)],
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
            yield prompt.found_spangram, spangram_str

        if len(found_theme_indices) > 0:
            yield (
                prompt.found_theme_words,
                self._format_words(
                    infos=map(final_result.answers.__getitem__, found_theme_indices)
                ),
            )

        if not spangram_found:
            yield prompt.missed_spangram, spangram_str

        if len(missed_theme_indices) > 0:
            yield (
                prompt.missed_theme_words,
                self._format_words(
                    infos=map(final_result.answers.__getitem__, missed_theme_indices)
                ),
            )

    def _format_words(self, *, infos: Iterable[tuple[str, list[tuple[int, int]]]]) -> str:
        return join_or_na(self._format_word(word=word, coords=coords) for word, coords in infos)

    def _format_word(self, *, word: str, coords: list[tuple[int, int]]) -> str:
        coords_str: str = " -> ".join(f"({x}, {y})" for x, y in coords)
        return f"{word} [{coords_str}]"
