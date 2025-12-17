from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from pydantic import BaseModel

from common.game import BaseGame
from llm.common import BaseLLM
from players.agent.player import BaseAgentPlayer, PromptMode


class BaseAgentGym[GT, PT, AT, RT, FT, ET: BaseModel](ABC):
    def play(self, model: BaseLLM, prompt_mode: PromptMode) -> None:
        player: BaseAgentPlayer[GT, PT, AT, RT, FT, ET] = self.create_player(
            model=model, prompt_mode=prompt_mode
        )

        if input("Train? (y/n): ")[0].lower() == "y":
            num_train_loops: int = 3
            num_in_loop_trials: int = 3

            for _ in range(num_train_loops):
                for i in range(num_in_loop_trials):
                    player.memory.reflect(
                        summary=self.create_game(select=False).play(player=player),
                        update_experience=i == num_in_loop_trials - 1,
                    )

        summary: FT = self.create_game(select=True).play(player=player)
        print("You Guessed", player.memory.num_guesses, "Times")
        self.summarize(summary=summary)
        player.memory.reflect(summary=summary, update_experience=False)

    @abstractmethod
    def create_player(
        self, *, model: BaseLLM, prompt_mode: PromptMode
    ) -> BaseAgentPlayer[GT, PT, AT, RT, FT, ET]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self, *, select: bool) -> BaseGame[GT, PT, AT, RT, FT]:
        raise NotImplementedError()

    @abstractmethod
    def summarize(self, *, summary: FT) -> None:
        raise NotImplementedError()


def build_contexto_agent_gym(seed: int) -> BaseAgentGym:
    from games.contexto.game import ContextoGameManager, ContextoResult
    from games.contexto.players.agent import ContextoAgentPlayer, ContextoExperience, ContextoMemory

    class ContextoAgentGym(
        BaseAgentGym[int, None, str, ContextoResult, list[str], ContextoExperience]
    ):
        def __init__(self) -> None:
            self._game_manager: ContextoGameManager = ContextoGameManager(seed=seed)
            self._max_guesses: int = int(input("Max Guesses: "))

        @override
        def create_player(
            self, *, model: BaseLLM, prompt_mode: PromptMode
        ) -> BaseAgentPlayer[int, None, str, ContextoResult, list[str], ContextoExperience]:
            return ContextoAgentPlayer(
                model=model,
                memory=ContextoMemory(model=model, experience_type=ContextoExperience),
                prompt_mode=prompt_mode,
            )

        @override
        def create_game(
            self, *, select: bool
        ) -> BaseGame[int, None, str, ContextoResult, list[str]]:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")) if select else None,
                max_guesses=self._max_guesses,
            )

        @override
        def summarize(self, *, summary: list[str]) -> None:
            print("Top Words:", *summary[:10])

    return ContextoAgentGym()


def build_contexto_hint_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from games.contexto_hint.game import ContextoHintGameManager
    from games.contexto_hint.players.agent import (
        ContextoHintAgentPlayer,
        ContextoHintExperience,
        ContextoHintMemory,
    )

    class ContextoHintAgentGym(
        BaseAgentGym[None, list[str], int, int, list[str], ContextoHintExperience]
    ):
        def __init__(self) -> None:
            self._game_manager: ContextoHintGameManager = ContextoHintGameManager(
                games_dir=Path("./data/contexto_hint/games"), seed=seed
            )

            self._num_candidates: int = int(input("Number of Candidates: "))

        @override
        def create_player(
            self, *, model: BaseLLM, prompt_mode: PromptMode
        ) -> BaseAgentPlayer[None, list[str], int, int, list[str], ContextoHintExperience]:
            return ContextoHintAgentPlayer(
                model=model,
                memory=ContextoHintMemory(model=model, experience_type=ContextoHintExperience),
                prompt_mode=prompt_mode,
            )

        @override
        def create_game(self, *, select: bool) -> BaseGame[None, list[str], int, int, list[str]]:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")) if select else None,
                num_candidates=self._num_candidates,
            )

        @override
        def summarize(self, *, summary: list[str]) -> None:
            print("Top Words:", *summary[:10])

    return ContextoHintAgentGym()


AGENT_GYM_BUILDERS: dict[str, Callable[[int], BaseAgentGym]] = {
    "contexto": build_contexto_agent_gym,
    "contexto-hint": build_contexto_hint_agent_gym,
}


def main():
    from time import time_ns

    from llm.openai import OpenAILLM

    games: list[str] = list(AGENT_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index + 1}. {game}")

    AGENT_GYM_BUILDERS[games[int(input("Game Index: ")) - 1]](time_ns()).play(
        model=OpenAILLM(
            api_key="sk-PInpH3EcNkJjwzqvB1EbBdF09e9b4b12A81fF0C325D55d71",
            base_url="https://openkey.cloud/v1",
            model=input("LLM Model: "),
            max_tokens=32768,
            timeout=7200,
        ),
        prompt_mode=(
            PromptMode.MULTI_TURN
            if input("Multi-turn? (y/n): ")[0].lower() == "y"
            else PromptMode.DIRECT
        )
        if input("Analyze? (y/n): ")[0].lower() == "y"
        else PromptMode.SIMPLE,
    )


if __name__ == "__main__":
    main()
