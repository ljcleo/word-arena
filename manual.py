from pathlib import Path
from time import time_ns

from contexto_hint.game import ContextoHintGameManager, ContextoHintGameResult
from contexto_hint.players.manual import ContextoHintManualPlayer


def main() -> None:
    result: ContextoHintGameResult = (
        ContextoHintGameManager(games_dir=Path("./contexto_hint/games"), seed=time_ns())
        .create_game(game_id=int(input("Input Game ID: ")), num_candidates=5)
        .play(player=ContextoHintManualPlayer())
    )

    print("You Guessed", len(result["trajectory"]), "Times")
    print("Top Words:", *result["summary"][:10])


if __name__ == "__main__":
    main()
