from build_gym import build_gym
from utils import input_game_key

from word_arena.common.gym.gym import Gym
from word_arena.common.player.player import Player


def main() -> None:
    game_key: str = input_game_key()
    gym: Gym = build_gym(game_key=game_key)
    player: Player

    if is_agent := input("Agent? (y/n): ")[0].lower() == "y":
        from build_agent_player import build_agent_player
        from utils import input_llm_key

        player = build_agent_player(game_key=game_key, llm_key=input_llm_key())
    else:
        from build_manual_player import build_manual_player

        player = build_manual_player(game_key=game_key)

    player.setup()

    if is_agent and input("Train? (y/n): ")[0].lower() == "y":
        from time import time_ns

        from word_arena.common.gym.common import TrainingConfig

        gym.train(
            player=player,
            training_config=TrainingConfig(
                num_train_loops=int(input("Number of Train Loops: ")),
                num_in_loop_trials=int(input("Number of In-Loop Trials: ")),
                seed=time_ns(),
            ),
        )

    gym.play(player=player)


if __name__ == "__main__":
    main()
