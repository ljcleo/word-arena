from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from pydantic import BaseModel

from word_arena.common.game.base import BaseGame
from word_arena.common.game.generator import BaseGameGenerator
from word_arena.common.llm.base import BaseLLM
from word_arena.common.player.agent.player import BaseAgentPlayer, PromptMode


class BaseAgentGym[ST, CT, IT, HT, GT: BaseModel, FT, RT, ET: BaseModel](ABC):
    def __init__(
        self, *, game_generator: BaseGameGenerator[ST, CT, BaseGame[IT, HT, GT, FT, RT]]
    ) -> None:
        self._game_generator: BaseGameGenerator[ST, CT, BaseGame[IT, HT, GT, FT, RT]] = (
            game_generator
        )

    def play(self, model: BaseLLM, prompt_mode: PromptMode) -> None:
        player: BaseAgentPlayer[IT, HT, GT, FT, RT, ET] = self.create_player(
            model=model, prompt_mode=prompt_mode
        )

        if input("Train? (y/n): ")[0].lower() == "y":
            num_train_loops: int = int(input("Number of Train Loops: "))
            num_in_loop_trials: int = int(input("Number of In-loop Trials: "))

            for _ in range(num_train_loops):
                for i in range(num_in_loop_trials):
                    player.memory.reflect(
                        final_result=self._game_generator.create_random_game().play(player=player),
                        update_experience=i == num_in_loop_trials - 1,
                    )

        final_result: RT = self._game_generator.create_game(config=self.create_config()).play(
            player=player
        )

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
    def create_config(self) -> CT:
        raise NotImplementedError()

    @abstractmethod
    def format_final_result(self, *, final_result: RT) -> Iterator[str]:
        raise NotImplementedError()


def build_contexto_agent_gym(seed: int) -> BaseAgentGym:
    from collections.abc import Iterable

    from word_arena.games.contexto.common import (
        ContextoExperience,
        ContextoFeedback,
        ContextoFinalResult,
        ContextoGuess,
    )
    from word_arena.games.contexto.formatter import ContextoFinalResultFormatter
    from word_arena.games.contexto.generator import (
        ContextoConfig,
        ContextoGameGenerator,
        ContextoSetting,
    )
    from word_arena.games.contexto.players.agent import ContextoAgentPlayer

    class ContextoAgentGym(
        BaseAgentGym[
            ContextoSetting,
            ContextoConfig,
            int,
            None,
            ContextoGuess,
            ContextoFeedback,
            ContextoFinalResult,
            ContextoExperience,
        ]
    ):
        def __init__(self, *, setting_pool: Iterable[ContextoSetting], seed: int) -> None:
            super().__init__(
                game_generator=ContextoGameGenerator(setting_pool=setting_pool, seed=seed)
            )

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ContextoAgentPlayer:
            return ContextoAgentPlayer(
                model=model,
                prompt_mode=prompt_mode,
            )

        @override
        def create_config(self) -> ContextoConfig:
            return ContextoConfig(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ContextoFinalResult) -> Iterator[str]:
            yield from ContextoFinalResultFormatter.format_final_result(final_result=final_result)

    return ContextoAgentGym(setting_pool=(ContextoSetting(max_guesses=50),), seed=seed)


def build_contexto_hint_agent_gym(seed: int) -> BaseAgentGym:
    from collections.abc import Iterable
    from pathlib import Path

    from word_arena.games.contexto_hint.common import ContextoHintExperience, ContextoHintGuess
    from word_arena.games.contexto_hint.formatter import ContextoHintFinalResultFormatter
    from word_arena.games.contexto_hint.generator import (
        ContextoHintConfig,
        ContextoHintGameGenerator,
        ContextoHintSetting,
    )
    from word_arena.games.contexto_hint.players.agent import ContextoHintAgentPlayer

    class ContextoHintAgentGym(
        BaseAgentGym[
            ContextoHintSetting,
            ContextoHintConfig,
            None,
            list[str],
            ContextoHintGuess,
            int,
            list[str],
            ContextoHintExperience,
        ]
    ):
        def __init__(
            self, *, setting_pool: Iterable[ContextoHintSetting], seed: int, games_dir: Path
        ) -> None:
            super().__init__(
                game_generator=ContextoHintGameGenerator(
                    setting_pool=setting_pool, seed=seed, games_dir=games_dir
                )
            )

        @override
        def create_player(
            self, *, model: BaseLLM, prompt_mode: PromptMode
        ) -> ContextoHintAgentPlayer:
            return ContextoHintAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_config(self) -> ContextoHintConfig:
            return ContextoHintConfig(
                game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
            )

        @override
        def format_final_result(self, *, final_result: list[str]) -> Iterator[str]:
            yield from ContextoHintFinalResultFormatter.format_final_result(
                final_result=final_result
            )

    return ContextoHintAgentGym(
        setting_pool=(ContextoHintSetting(num_candidates=5),),
        seed=seed,
        games_dir=Path("./data/contexto_hint/games"),
    )


def build_wordle_agent_gym(seed: int) -> BaseAgentGym:
    from collections.abc import Iterable
    from pathlib import Path

    from word_arena.games.wordle.common import (
        WordleExperience,
        WordleFeedback,
        WordleFinalResult,
        WordleGuess,
        WordleInfo,
    )
    from word_arena.games.wordle.formatter import WordleFinalResultFormatter
    from word_arena.games.wordle.generator import WordleConfig, WordleGameGenerator, WordleSetting
    from word_arena.games.wordle.players.agent import WordleAgentPlayer

    class WordleAgentGym(
        BaseAgentGym[
            WordleSetting,
            WordleConfig,
            WordleInfo,
            None,
            WordleGuess,
            WordleFeedback,
            WordleFinalResult,
            WordleExperience,
        ]
    ):
        def __init__(
            self, *, setting_pool: Iterable[WordleSetting], seed: int, word_list_file: Path
        ) -> None:
            game_generator: WordleGameGenerator = WordleGameGenerator(
                setting_pool=setting_pool, seed=seed, word_list_file=word_list_file
            )

            super().__init__(game_generator=game_generator)
            self._word_list: list[str] = game_generator._word_list

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> WordleAgentPlayer:
            return WordleAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_config(self) -> WordleConfig:
            return WordleConfig(
                word_list=self._word_list,
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def format_final_result(self, *, final_result: WordleFinalResult) -> Iterator[str]:
            yield from WordleFinalResultFormatter.format_final_result(final_result=final_result)

    return WordleAgentGym(
        setting_pool=(
            WordleSetting(num_targets=num_targets, max_guesses=num_targets + 5)
            for num_targets in (1, 2, 4, 8, 16)
        ),
        seed=seed,
        word_list_file=Path("./data/wordle/words.txt"),
    )


def build_letroso_agent_gym(seed: int) -> BaseAgentGym:
    from collections.abc import Iterable
    from pathlib import Path

    from word_arena.games.letroso.common import (
        LetrosoExperience,
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoGuess,
        LetrosoInfo,
    )
    from word_arena.games.letroso.formatter import LetrosoFinalResultFormatter
    from word_arena.games.letroso.generator import (
        LetrosoConfig,
        LetrosoGameGenerator,
        LetrosoSetting,
    )
    from word_arena.games.letroso.players.agent import LetrosoAgentPlayer

    class LetrosoAgentGym(
        BaseAgentGym[
            LetrosoSetting,
            LetrosoConfig,
            LetrosoInfo,
            None,
            LetrosoGuess,
            LetrosoFeedback,
            LetrosoFinalResult,
            LetrosoExperience,
        ]
    ):
        def __init__(
            self, *, setting_pool: Iterable[LetrosoSetting], seed: int, word_list_file: Path
        ) -> None:
            game_generator: LetrosoGameGenerator = LetrosoGameGenerator(
                setting_pool=setting_pool, seed=seed, word_list_file=word_list_file
            )

            super().__init__(game_generator=game_generator)
            self._word_list: list[str] = game_generator._word_list

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> LetrosoAgentPlayer:
            return LetrosoAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_config(self) -> LetrosoConfig:
            return LetrosoConfig(
                word_list=self._word_list,
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_letters=int(input("Max Input Letters: ")),
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def format_final_result(self, *, final_result: LetrosoFinalResult) -> Iterator[str]:
            yield from LetrosoFinalResultFormatter.format_final_result(final_result=final_result)

    return LetrosoAgentGym(
        setting_pool=(LetrosoSetting(num_targets=1, max_letters=10, max_guesses=20),),
        seed=seed,
        word_list_file=Path("./data/letroso/words.txt"),
    )


def build_conexo_agent_gym(seed: int) -> BaseAgentGym:
    from collections.abc import Iterable
    from pathlib import Path

    from word_arena.games.conexo.common import (
        ConexoExperience,
        ConexoFeedback,
        ConexoFinalResult,
        ConexoGuess,
        ConexoInfo,
    )
    from word_arena.games.conexo.formatter import ConexoFinalResultFormatter
    from word_arena.games.conexo.generator import ConexoConfig, ConexoGameGenerator, ConexoSetting
    from word_arena.games.conexo.players.agent import ConexoAgentPlayer

    class ConexoAgentGym(
        BaseAgentGym[
            ConexoSetting,
            ConexoConfig,
            ConexoInfo,
            None,
            ConexoGuess,
            ConexoFeedback,
            ConexoFinalResult,
            ConexoExperience,
        ]
    ):
        def __init__(
            self, *, setting_pool: Iterable[ConexoSetting], seed: int, games_dir: Path
        ) -> None:
            super().__init__(
                game_generator=ConexoGameGenerator(
                    setting_pool=setting_pool, seed=seed, games_dir=games_dir
                )
            )

        @override
        def create_player(self, *, model: BaseLLM, prompt_mode: PromptMode) -> ConexoAgentPlayer:
            return ConexoAgentPlayer(model=model, prompt_mode=prompt_mode)

        @override
        def create_config(self) -> ConexoConfig:
            return ConexoConfig(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ConexoFinalResult) -> Iterator[str]:
            yield from ConexoFinalResultFormatter.format_final_result(final_result=final_result)

    return ConexoAgentGym(
        setting_pool=(ConexoSetting(max_guesses=20),),
        seed=seed,
        games_dir=Path("./data/conexo/games"),
    )


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
