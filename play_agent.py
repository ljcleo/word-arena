from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from pydantic import BaseModel

from word_arena.common.game.base import BaseGame
from word_arena.common.llm.base import BaseLLM
from word_arena.common.player.agent.player import BaseAgentPlayer, PromptMode


class BaseAgentGym[IT, HT, GT, FT, RT, ET: BaseModel](ABC):
    def play(self, model: BaseLLM, prompt_mode: PromptMode) -> None:
        player: BaseAgentPlayer[IT, HT, GT, FT, RT, ET] = self.create_player(
            model=model, prompt_mode=prompt_mode
        )

        if input("Train? (y/n): ")[0].lower() == "y":
            num_train_loops: int = 3
            num_in_loop_trials: int = 3

            for _ in range(num_train_loops):
                for i in range(num_in_loop_trials):
                    player.memory.reflect(
                        final_result=self.create_game(select=False).play(player=player),
                        update_experience=i == num_in_loop_trials - 1,
                    )

        final_result: RT = self.create_game(select=True).play(player=player)
        print("You Guessed", player.memory.num_guesses, "Times")

        for section in self.format_final_result(final_result=final_result):
            print(section)

        player.memory.reflect(final_result=final_result, update_experience=False)

    @abstractmethod
    def create_player(
        self, *, model: BaseLLM, prompt_mode: PromptMode
    ) -> BaseAgentPlayer[IT, HT, GT, FT, RT, ET]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self, *, select: bool) -> BaseGame[IT, HT, GT, FT, RT]:
        raise NotImplementedError()

    @abstractmethod
    def format_final_result(self, *, final_result: RT) -> Iterator[str]:
        raise NotImplementedError()


def build_contexto_agent_gym(seed: int) -> BaseAgentGym:
    from word_arena.games.contexto.common import (
        ContextoExperience,
        ContextoFeedback,
        ContextoFinalResult,
    )
    from word_arena.games.contexto.formatter import ContextoFinalResultFormatter
    from word_arena.games.contexto.game import ContextoGame, ContextoGameManager
    from word_arena.games.contexto.players.agent import ContextoAgentPlayer

    class ContextoAgentGym(
        BaseAgentGym[int, None, str, ContextoFeedback, ContextoFinalResult, ContextoExperience]
    ):
        def __init__(self) -> None:
            self._game_manager: ContextoGameManager = ContextoGameManager(seed=seed)
            self._max_guesses: int = int(input("Max Guesses: "))

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ContextoAgentPlayer:
            return ContextoAgentPlayer(
                model=model,
                prompt_mode=prompt_mode,
            )

        @override
        def create_game(self, *, select: bool) -> ContextoGame:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")) if select else None,
                max_guesses=self._max_guesses,
            )

        @override
        def format_final_result(self, *, final_result: ContextoFinalResult) -> Iterator[str]:
            yield from ContextoFinalResultFormatter.format_final_result(final_result=final_result)

    return ContextoAgentGym()


def build_contexto_hint_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.common import ContextoHintExperience
    from word_arena.games.contexto_hint.formatter import ContextoHintFinalResultFormatter
    from word_arena.games.contexto_hint.game import ContextoHintGame, ContextoHintGameManager
    from word_arena.games.contexto_hint.players.agent import ContextoHintAgentPlayer

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
        ) -> ContextoHintAgentPlayer:
            return ContextoHintAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_game(self, *, select: bool) -> ContextoHintGame:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")) if select else None,
                num_candidates=self._num_candidates,
            )

        @override
        def format_final_result(self, *, final_result: list[str]) -> Iterator[str]:
            yield from ContextoHintFinalResultFormatter.format_final_result(
                final_result=final_result
            )

    return ContextoHintAgentGym()


def build_wordle_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.wordle.common import (
        WordleExperience,
        WordleFeedback,
        WordleFinalResult,
        WordleInfo,
    )
    from word_arena.games.wordle.formatter import WordleFinalResultFormatter
    from word_arena.games.wordle.game import WordleGameManager
    from word_arena.games.wordle.players.agent import WordleAgentPlayer

    class WordleAgentGym(
        BaseAgentGym[WordleInfo, None, str, WordleFeedback, WordleFinalResult, WordleExperience]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: WordleGameManager = WordleGameManager(
                word_list_file=Path("./data/wordle/words.txt"), seed=seed
            )

        @override
        def create_player(
            self, *, model: BaseLLM, prompt_mode: PromptMode
        ) -> BaseAgentPlayer[
            WordleInfo, None, str, WordleFeedback, WordleFinalResult, WordleExperience
        ]:
            return WordleAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_game(
            self, *, select: bool
        ) -> BaseGame[WordleInfo, None, str, WordleFeedback, WordleFinalResult]:
            return (
                self._game_manager.create_game(
                    target_ids=[
                        int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                    ],
                    max_guesses=int(input("Max Guesses: ")),
                )
                if select
                else self._game_manager.create_random_game(
                    param_candidates=[(1, 6), (2, 7), (4, 9), (8, 13)]
                )
            )

        @override
        def format_final_result(self, *, final_result: WordleFinalResult) -> Iterator[str]:
            yield from WordleFinalResultFormatter.format_final_result(final_result=final_result)

    return WordleAgentGym(seed=seed)


def build_letroso_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.letroso.common import (
        LetrosoExperience,
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoInfo,
    )
    from word_arena.games.letroso.formatter import LetrosoFinalResultFormatter
    from word_arena.games.letroso.game import LetrosoGame, LetrosoGameManager
    from word_arena.games.letroso.players.agent import LetrosoAgentPlayer

    class LetrosoAgentGym(
        BaseAgentGym[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult, LetrosoExperience]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: LetrosoGameManager = LetrosoGameManager(
                word_list_file=Path("./data/letroso/words.txt"), seed=seed
            )

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> LetrosoAgentPlayer:
            return LetrosoAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_game(self, *, select: bool) -> LetrosoGame:
            return (
                self._game_manager.create_game(
                    target_ids=[
                        int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                    ],
                    max_letters=int(input("Max Input Letters: ")),
                    max_guesses=int(input("Max Guesses: ")),
                )
                if select
                else self._game_manager.create_random_game(param_candidates=[(1, 10, 20)])
            )

        @override
        def format_final_result(self, *, final_result: LetrosoFinalResult) -> Iterator[str]:
            yield from LetrosoFinalResultFormatter.format_final_result(final_result=final_result)

    return LetrosoAgentGym(seed=seed)


def build_conexo_agent_gym(seed: int) -> BaseAgentGym:
    from pathlib import Path

    from word_arena.games.conexo.common import (
        ConexoExperience,
        ConexoFeedback,
        ConexoFinalResult,
        ConexoInfo,
    )
    from word_arena.games.conexo.formatter import ConexoFinalResultFormatter
    from word_arena.games.conexo.game import ConexoGame, ConexoGameManager
    from word_arena.games.conexo.players.agent import ConexoAgentPlayer

    class ConexoAgentGym(
        BaseAgentGym[
            ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult, ConexoExperience
        ]
    ):
        def __init__(self) -> None:
            self._game_manager: ConexoGameManager = ConexoGameManager(
                games_dir=Path("./data/conexo/games"), seed=seed
            )

            self._max_guesses: int = int(input("Max Guesses: "))

        @override
        def create_player(
            self, *, model: BaseLLM, prompt_mode: PromptMode
        ) -> BaseAgentPlayer[
            ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult, ConexoExperience
        ]:
            return ConexoAgentPlayer(
                model=model,
                prompt_mode=prompt_mode,
            )

        @override
        def create_game(self, *, select: bool) -> ConexoGame:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")) if select else None,
                max_guesses=self._max_guesses,
            )

        @override
        def format_final_result(self, *, final_result: ConexoFinalResult) -> Iterator[str]:
            yield from ConexoFinalResultFormatter.format_final_result(final_result=final_result)

    return ConexoAgentGym()


AGENT_GYM_BUILDERS: dict[str, Callable[[int], BaseAgentGym]] = {
    "contexto": build_contexto_agent_gym,
    "contexto-hint": build_contexto_hint_agent_gym,
    "wordle": build_wordle_agent_gym,
    "letroso": build_letroso_agent_gym,
    "conexo": build_conexo_agent_gym,
}


def main():
    from time import time_ns

    from word_arena.llms.openai import OpenAILLM

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
            use_dev_message=True,
            log_file="llm.log",
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
