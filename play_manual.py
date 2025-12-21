from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from word_arena.common.game.base import BaseGame
from word_arena.common.game.generator import BaseGameProvider
from word_arena.common.player.manual import BaseManualPlayer


class BaseManualGym[CT, IT, HT, GT, FT, RT](ABC):
    def __init__(
        self, *, game_provider: BaseGameProvider[CT, BaseGame[IT, HT, GT, FT, RT]]
    ) -> None:
        self._game_provider: BaseGameProvider[CT, BaseGame[IT, HT, GT, FT, RT]] = game_provider

    def play(self) -> None:
        player: BaseManualPlayer[IT, HT, GT, FT] = self.create_player()

        final_result: RT = self._game_provider.create_game(config=self.create_config()).play(
            player=player
        )

        print("You Guessed", player.num_guesses, "Times")

        for section in self.format_final_result(final_result=final_result):
            print(section)

    @abstractmethod
    def create_player(self) -> BaseManualPlayer[IT, HT, GT, FT]:
        raise NotImplementedError()

    @abstractmethod
    def create_config(self) -> CT:
        raise NotImplementedError()

    @abstractmethod
    def format_final_result(self, *, final_result: RT) -> Iterator[str]:
        raise NotImplementedError()


def build_contexto_manual_gym() -> BaseManualGym:
    from word_arena.games.contexto.common import (
        ContextoFeedback,
        ContextoFinalResult,
        ContextoGuess,
    )
    from word_arena.games.contexto.formatter import ContextoFinalResultFormatter
    from word_arena.games.contexto.generator import ContextoConfig, ContextoGameProvider
    from word_arena.games.contexto.players.manual import ContextoManualPlayer

    class ContextoManualGym(
        BaseManualGym[
            ContextoConfig, int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult
        ]
    ):
        def __init__(self) -> None:
            super().__init__(game_provider=ContextoGameProvider())

        @override
        def create_player(self) -> ContextoManualPlayer:
            return ContextoManualPlayer()

        @override
        def create_config(self) -> ContextoConfig:
            return ContextoConfig(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ContextoFinalResult) -> Iterator[str]:
            yield from ContextoFinalResultFormatter.format_final_result(final_result=final_result)

    return ContextoManualGym()


def build_contexto_hint_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.common import ContextoHintGuess
    from word_arena.games.contexto_hint.formatter import ContextoHintFinalResultFormatter
    from word_arena.games.contexto_hint.generator import (
        ContextoHintConfig,
        ContextoHintGameProvider,
    )
    from word_arena.games.contexto_hint.players.manual import ContextoHintManualPlayer

    class ContextoHintManualGym(
        BaseManualGym[ContextoHintConfig, None, list[str], ContextoHintGuess, int, list[str]]
    ):
        def __init__(self, *, games_dir: Path) -> None:
            super().__init__(game_provider=ContextoHintGameProvider(games_dir=games_dir))

        @override
        def create_player(self) -> ContextoHintManualPlayer:
            return ContextoHintManualPlayer()

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

    return ContextoHintManualGym(games_dir=Path("./data/contexto_hint/games"))


def build_wordle_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.wordle.common import (
        WordleFeedback,
        WordleFinalResult,
        WordleGuess,
        WordleInfo,
    )
    from word_arena.games.wordle.formatter import WordleFinalResultFormatter
    from word_arena.games.wordle.generator import WordleConfig, WordleGameProvider
    from word_arena.games.wordle.players.manual import WordleManualPlayer

    class WordleManualGym(
        BaseManualGym[
            WordleConfig, WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult
        ]
    ):
        def __init__(self, *, word_list_path: Path) -> None:
            super().__init__(game_provider=WordleGameProvider())
            with word_list_path.open(encoding="utf8") as f:
                self._word_list: list[str] = list(map(str.strip, f))

        @override
        def create_player(self) -> WordleManualPlayer:
            return WordleManualPlayer()

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

    return WordleManualGym(word_list_path=Path("./data/wordle/words.txt"))


def build_letroso_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.letroso.common import (
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoGuess,
        LetrosoInfo,
    )
    from word_arena.games.letroso.formatter import LetrosoFinalResultFormatter
    from word_arena.games.letroso.generator import LetrosoConfig, LetrosoGameProvider
    from word_arena.games.letroso.players.manual import LetrosoManualPlayer

    class LetrosoManualGym(
        BaseManualGym[
            LetrosoConfig, LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult
        ]
    ):
        def __init__(self, *, word_list_path: Path) -> None:
            super().__init__(game_provider=LetrosoGameProvider())
            with word_list_path.open(encoding="utf8") as f:
                self._word_list: list[str] = list(map(str.strip, f))

        @override
        def create_player(self) -> LetrosoManualPlayer:
            return LetrosoManualPlayer()

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

    return LetrosoManualGym(word_list_path=Path("./data/letroso/words.txt"))


def build_conexo_manual_gym() -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.conexo.common import (
        ConexoFeedback,
        ConexoFinalResult,
        ConexoGuess,
        ConexoInfo,
    )
    from word_arena.games.conexo.formatter import ConexoFinalResultFormatter
    from word_arena.games.conexo.generator import ConexoConfig, ConexoGameProvider
    from word_arena.games.conexo.players.manual import ConexoManualPlayer

    class ConexoManualGym(
        BaseManualGym[
            ConexoConfig, ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult
        ]
    ):
        def __init__(self, *, games_dir: Path) -> None:
            super().__init__(game_provider=ConexoGameProvider(games_dir=games_dir))

        @override
        def create_player(self) -> ConexoManualPlayer:
            return ConexoManualPlayer()

        @override
        def create_config(self) -> ConexoConfig:
            return ConexoConfig(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ConexoFinalResult) -> Iterator[str]:
            yield from ConexoFinalResultFormatter.format_final_result(final_result=final_result)

    return ConexoManualGym(games_dir=Path("./data/conexo/games"))


MANUAL_GYM_BUILDERS: dict[str, Callable[[], BaseManualGym]] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
    "letroso": build_letroso_manual_gym,
    "conexo": build_conexo_manual_gym,
}


def main():
    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index + 1}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: ")) - 1]]().play()


if __name__ == "__main__":
    main()
