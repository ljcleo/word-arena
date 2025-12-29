from collections.abc import Iterable, Iterator
from typing import override

from ....common.formatter.base import BaseFinalResultFormatter, BaseInGameFormatter
from ..common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo


class StrandsInGameFormatter(BaseInGameFormatter[StrandsInfo, None, StrandsGuess, StrandsFeedback]):
    @override
    @classmethod
    def format_game_info(cls, *, game_info: StrandsInfo) -> Iterator[tuple[str, str]]:
        yield "Board", "\n".join(game_info.board)
        yield "Clue", game_info.clue

        yield (
            "Maximum Number of Guesses",
            "Unlimited" if game_info.max_guesses <= 0 else str(game_info.max_guesses),
        )

    @override
    @classmethod
    def format_hint(cls, *, game_info: StrandsInfo, hint: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    @classmethod
    def format_guess(
        cls, *, game_info: StrandsInfo, hint: None, guess: StrandsGuess
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

    @override
    @classmethod
    def format_feedback(
        cls, *, game_info: StrandsInfo, hint: None, guess: StrandsGuess, feedback: StrandsFeedback
    ) -> Iterator[tuple[str, str]]:
        if isinstance(feedback, int):
            yield "Validation Result", "Accept"
            yield "Guess Result", ("Missed", "Theme Word", "Spangram")[feedback]
        else:
            yield "Validation Result", "Reject"
            yield "Reason", feedback


class StrandsFinalResultFormatter(BaseFinalResultFormatter[StrandsFinalResult]):
    @override
    @classmethod
    def format_final_result(cls, *, final_result: StrandsFinalResult) -> Iterator[tuple[str, str]]:
        yield (
            "Game Result",
            "Victory" if len(final_result.found_indices) == len(final_result.answers) else "Failed",
        )

        spangram_str: str = cls._format_words(infos=final_result.answers[:1])
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
                cls._format_words(infos=map(final_result.answers.__getitem__, found_theme_indices)),
            )

        if not spangram_found:
            yield "Spangram Not Found", spangram_str

        if len(missed_theme_indices) > 0:
            yield (
                "Theme Words Not Found",
                cls._format_words(
                    infos=map(final_result.answers.__getitem__, missed_theme_indices)
                ),
            )

    @classmethod
    def _format_words(cls, *, infos: Iterable[tuple[str, list[tuple[int, int]]]]) -> str:
        return "; ".join(cls._format_word(word=word, coords=coords) for word, coords in infos)

    @classmethod
    def _format_word(cls, *, word: str, coords: list[tuple[int, int]]) -> str:
        coords_str: str = " -> ".join(f"({x}, {y})" for x, y in coords)
        return f"{word} [{coords_str}]"
