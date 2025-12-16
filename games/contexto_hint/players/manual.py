from typing import override

from common.player import BasePlayer


class ContextoHintManualPlayer(BasePlayer[int, list[str], int, int]):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: int) -> None:
        self._game_info: int = game_info
        self._num_guesses: int = 0

    @override
    def guess(self, *, hint: list[str]) -> int:
        print("Candidates:")
        print(*(f"{chr(i + ord('A'))}: {candidate}" for i, candidate in enumerate(hint)))
        return ord(input("Guess Choice: ")) - ord("A")

    @override
    def digest(self, *, hint: list[str], guess: int, result: int) -> None:
        print("Guess:", hint[guess], "Position:", result + 1)
        self._num_guesses += 1


def main() -> None:
    from pathlib import Path
    from time import time_ns

    from games.contexto_hint.game import ContextoHintGameManager

    player: ContextoHintManualPlayer = ContextoHintManualPlayer()

    summary: list[str] = (
        ContextoHintGameManager(games_dir=Path("data/contexto_hint/games"), seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")), num_candidates=5)
        .play(player=player)
    )

    print("You Guessed", player.num_guesses, "Times")
    print("Top Words:", *summary[:10])


if __name__ == "__main__":
    main()
