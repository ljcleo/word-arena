from build_gym import GYM_BUILDERS, build_gym
from build_manual_player import build_player


def main() -> None:
    games: list[str] = list(GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index}. {game}")

    game_key: str = games[int(input("Game Index: "))]
    build_gym(game_key=game_key).play(player=build_player(game_key=game_key))


if __name__ == "__main__":
    main()
