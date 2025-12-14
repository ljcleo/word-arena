from typing import override

from common.player import BasePlayer


class ContextoHintManualPlayer(BasePlayer[int, list[str], int, int]):
    @override
    def prepare(self, *, game_info: int) -> None:
        pass

    @override
    def guess(self, *, hint: list[str]) -> int:
        print("Candidates:")
        print(*(f"{chr(i + ord('A'))}: {candidate}" for i, candidate in enumerate(hint)))
        return ord(input("Guess Choice: ")) - ord("A")

    @override
    def digest(self, *, hint: list[str], guess: int, result: int) -> None:
        print("Guess:", hint[guess], "Position:", result + 1)


def main() -> None:
    from pathlib import Path
    from time import time_ns

    from games.contexto_hint.game import ContextoHintGameManager, ContextoHintGameResult

    result: ContextoHintGameResult = (
        ContextoHintGameManager(games_dir=Path("data/contexto_hint/games"), seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")), num_candidates=5)
        .play(player=ContextoHintManualPlayer())
    )

    print("You Guessed", len(result["trajectory"]), "Times")
    print("Top Words:", *result["summary"][:10])


if __name__ == "__main__":
    main()
