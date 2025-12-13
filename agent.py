from pathlib import Path
from time import time_ns

from openai import OpenAI

from contexto_hint.game import ContextoHintGameManager, ContextoHintGameResult
from contexto_hint.players.agent import ContextoHintAgentPlayer, PromptMode
from llm.openai import OpenAILLM


def main() -> None:
    model: OpenAILLM = OpenAILLM(
        client=OpenAI(
            api_key="sk-PInpH3EcNkJjwzqvB1EbBdF09e9b4b12A81fF0C325D55d71",
            base_url="https://openkey.cloud/v1",
        ),
        model="gpt-5-mini",
        max_tokens=32768,
        timeout=7200,
    )

    player = ContextoHintAgentPlayer(model=model, prompt_mode=PromptMode.MULTI_TURN)

    game_manager: ContextoHintGameManager = ContextoHintGameManager(
        games_dir=Path("./contexto_hint/games"), seed=time_ns()
    )

    if input("Train? (y/n): ")[0].lower() == "y":
        num_train_loops: int = 3
        num_in_loop_trials: int = 3

        for _ in range(num_train_loops):
            for i in range(num_in_loop_trials):
                result: ContextoHintGameResult = game_manager.create_game(
                    game_id=None, num_candidates=5
                ).play(player=player)

                player.memory.reflect(
                    summary=result["summary"], update_experience=i == num_in_loop_trials - 1
                )

    result = game_manager.create_game(game_id=int(input("Input Game ID: ")), num_candidates=5).play(
        player=player
    )

    print("You Guessed", len(result["trajectory"]), "Times")
    print("Top Words:", *result["summary"][:10])


if __name__ == "__main__":
    main()
