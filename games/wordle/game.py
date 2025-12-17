from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from random import Random
from typing import override

from common.game import BaseGame
from games.wordle.common import WordleResult


class WordleGame(BaseGame[None, None, str, WordleResult, str]):
    def __init__(self, *, word_list: Sequence[str], game_id: int) -> None:
        self._word_list: set[str] = set(word_list)
        self._answer: str = word_list[game_id]

    @override
    def start_game(self) -> None:
        self._num_guesses: int = 0
        self._solved: bool = False

    @override
    def is_over(self) -> bool:
        return self._solved or self._num_guesses >= 6

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: str) -> WordleResult:
        if not (len(guess) == len(self._answer) and guess.isalpha() and guess.islower()):
            return {"accepted": False, "result": "Invalid guess"}
        elif guess not in self._word_list:
            return {"accepted": False, "result": "Unknown word"}

        self._num_guesses += 1
        if guess == self._answer:
            self._solved = True

        buffer = ["B"] * len(self._answer)
        counter: Counter = Counter(self._answer)

        for i, (x, y) in enumerate(zip(guess, self._answer)):
            if x == y:
                buffer[i] = "G"
                counter[y] -= 1

        for i, x in enumerate(guess):
            if buffer[i] != "G" and counter[x] > 0:
                buffer[i] = "Y"
                counter[x] -= 1

        return {"accepted": True, "result": "".join(buffer)}

    @override
    def summarize_game(self) -> str:
        return self._answer


class WordleGameManager:
    def __init__(self, *, word_list_file: Path, seed: int) -> None:
        with word_list_file.open(encoding="utf8") as f:
            self._word_list: list[str] = list(map(str.strip, f))

        self._num_games: int = len(self._word_list)
        self._rng: Random = Random(seed)

    def create_game(self, *, game_id: int | None) -> WordleGame:
        if game_id is None:
            game_id = self._rng.randrange(self._num_games)
            print("Current Game ID:", game_id)

        return WordleGame(word_list=self._word_list, game_id=game_id)
