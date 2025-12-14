from typing import override

from common.player import BasePlayer
from games.contexto.common import ContextoError, ContextoResponse


class ContextoManualPlayer(BasePlayer[None, None, str, ContextoResponse | ContextoError]):
    @override
    def prepare(self, *, game_info: None) -> None:
        pass

    @override
    def guess(self, *, hint: None) -> str:
        return input("Guess: ")

    @override
    def digest(self, *, hint: None, guess: str, result: ContextoResponse | ContextoError) -> None:
        print("Guess:", guess, "Result:", result.model_dump_json())


def main() -> None:
    from time import time_ns

    from games.contexto.game import ContextoGameManager, ContextoGameResult

    result: ContextoGameResult = (
        ContextoGameManager(seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")))
        .play(player=ContextoManualPlayer())
    )

    print("You Guessed", len(result["trajectory"]), "Times")
    print("Top Words:", *result["summary"][:10])


if __name__ == "__main__":
    main()
