from build_gym import build_gym
from build_manual_player import build_player
from utils import input_game_key


def main() -> None:
    game_key: str = input_game_key()
    build_gym(game_key=game_key).play(player=build_player(game_key=game_key))


if __name__ == "__main__":
    main()
