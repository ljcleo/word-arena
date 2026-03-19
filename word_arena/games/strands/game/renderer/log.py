from collections.abc import Iterable, Iterator
from typing import override

from .....common.game.renderer.log import BaseLogGameRenderer
from ...common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ..common import StrandsGameStateInterface


class StrandsLogGameRenderer(
    BaseLogGameRenderer[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult]
):
    @override
    def format_game_info(self, *, state: StrandsGameStateInterface) -> Iterator[tuple[str, str]]:
        game_info: StrandsInfo = state.game_info
        yield "Board", "\n".join(game_info.board)
        yield "Clue", game_info.clue

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_turns <= 0 else str(game_info.max_turns),
        )

    @override
    def format_guess(
        self, *, state: StrandsGameStateInterface, guess: StrandsGuess
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

            buffer.append(state.game_info.board[cx][cy])
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

    @override
    def format_last_feedback(
        self, *, state: StrandsGameStateInterface
    ) -> Iterator[tuple[str, str]]:
        feedback: StrandsFeedback = state.turns[-1].feedback

        if isinstance(feedback, int):
            yield "Validation Result", "Accept"
            yield "Guess Result", ("Missed", "Theme Word", "Spangram")[feedback]
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback

    @override
    def format_final_result(self, *, state: StrandsGameStateInterface) -> Iterator[tuple[str, str]]:
        final_result: StrandsFinalResult = state.final_result

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

    def _format_words(self, *, infos: Iterable[tuple[str, list[tuple[int, int]]]]) -> str:
        return "; ".join(self._format_word(word=word, coords=coords) for word, coords in infos)

    def _format_word(self, *, word: str, coords: list[tuple[int, int]]) -> str:
        coords_str: str = " -> ".join(f"({x}, {y})" for x, y in coords)
        return f"{word} [{coords_str}]"
