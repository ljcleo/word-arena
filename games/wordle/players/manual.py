from typing import override

from common.player import BasePlayer
from games.wordle.common import WordleResult


class WordleManualPlayer(BasePlayer[None, None, str, WordleResult]):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: None) -> None:
        self._num_guesses: int = 0

    @override
    def guess(self, *, hint: None) -> str:
        return input("Guess: ")

    @override
    def digest(self, *, hint: None, guess: str, result: WordleResult) -> None:
        if result["accepted"]:
            print("Guess:", guess, "Result:", result["result"])
            self._num_guesses += 1
        else:
            print(result["result"])


def main() -> None:
    from pathlib import Path
    from time import time_ns

    from games.wordle.game import WordleGameManager

    player: WordleManualPlayer = WordleManualPlayer()

    summary: str = (
        WordleGameManager(word_list_file=Path("data/wordle/words.txt"), seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")))
        .play(player=player)
    )

    print("You Guessed", player.num_guesses, "Times")
    print("Answer:", summary)


if __name__ == "__main__":
    main()
