from typing import override

from common.player import BasePlayer
from games.contexto.common import ContextoError, ContextoResponse


class ContextoManualPlayer(BasePlayer[int, None, str, ContextoResponse | ContextoError]):
    @property
    def num_guesses(self) -> int:
        return self._num_guesses

    @override
    def prepare(self, *, game_info: int) -> None:
        self._num_guesses: int = 0

    @override
    def guess(self, *, hint: None) -> str:
        return input("Guess: ")

    @override
    def digest(self, *, hint: None, guess: str, result: ContextoResponse | ContextoError) -> None:
        print("Guess:", guess, "Result:", result.model_dump_json())
        self._num_guesses += 1


def main() -> None:
    from time import time_ns

    from games.contexto.game import ContextoGameManager

    player: ContextoManualPlayer = ContextoManualPlayer()

    summary: list[str] = (
        ContextoGameManager(seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")), max_guesses=0)
        .play(player=player)
    )

    print("You Guessed", player.num_guesses, "Times")
    print("Top Words:", *summary[:10])


if __name__ == "__main__":
    main()
