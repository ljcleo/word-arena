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
