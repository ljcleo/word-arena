from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import override

from word_arena.common.game.base import BaseGame
from word_arena.common.player.manual import BaseManualPlayer


class BaseManualGym[IT, HT, GT, FT, RT](ABC):
    def play(self) -> None:
        player: BaseManualPlayer[IT, HT, GT, FT] = self.create_player()
        final_result: RT = self.create_game().play(player=player)
        print("You Guessed", player.num_guesses, "Times")

        for section in self.format_final_result(final_result=final_result):
            print(section)

    @abstractmethod
    def create_player(self) -> BaseManualPlayer[IT, HT, GT, FT]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self) -> BaseGame[IT, HT, GT, FT, RT]:
        raise NotImplementedError()

    @abstractmethod
    def format_final_result(self, *, final_result: RT) -> Iterator[str]:
        raise NotImplementedError()


def build_contexto_manual_gym(seed: int) -> BaseManualGym:
    from word_arena.games.contexto.common import (
        ContextoFeedback,
        ContextoFinalResult,
        ContextoGuess,
    )
    from word_arena.games.contexto.formatter import ContextoFinalResultFormatter
    from word_arena.games.contexto.game import ContextoGame, ContextoGameManager
    from word_arena.games.contexto.players.manual import ContextoManualPlayer

    class ContextoManualGym(
        BaseManualGym[int, None, ContextoGuess, ContextoFeedback, ContextoFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ContextoGameManager = ContextoGameManager(seed=seed)

        @override
        def create_player(self) -> ContextoManualPlayer:
            return ContextoManualPlayer()

        @override
        def create_game(self) -> ContextoGame:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ContextoFinalResult) -> Iterator[str]:
            yield from ContextoFinalResultFormatter.format_final_result(final_result=final_result)

    return ContextoManualGym(seed=seed)


def build_contexto_hint_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.contexto_hint.common import ContextoHintGuess
    from word_arena.games.contexto_hint.formatter import ContextoHintFinalResultFormatter
    from word_arena.games.contexto_hint.game import ContextoHintGame, ContextoHintGameManager
    from word_arena.games.contexto_hint.players.manual import ContextoHintManualPlayer

    class ContextoHintManualGym(BaseManualGym[None, list[str], ContextoHintGuess, int, list[str]]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ContextoHintGameManager = ContextoHintGameManager(
                games_dir=Path("./data/contexto_hint/games"), seed=seed
            )

        @override
        def create_player(self) -> ContextoHintManualPlayer:
            return ContextoHintManualPlayer()

        @override
        def create_game(self) -> ContextoHintGame:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
            )

        @override
        def format_final_result(self, *, final_result: list[str]) -> Iterator[str]:
            yield from ContextoHintFinalResultFormatter.format_final_result(
                final_result=final_result
            )

    return ContextoHintManualGym(seed=seed)


def build_wordle_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.wordle.common import (
        WordleFeedback,
        WordleFinalResult,
        WordleGuess,
        WordleInfo,
    )
    from word_arena.games.wordle.formatter import WordleFinalResultFormatter
    from word_arena.games.wordle.game import WordleGame, WordleGameManager
    from word_arena.games.wordle.players.manual import WordleManualPlayer

    class WordleManualGym(
        BaseManualGym[WordleInfo, None, WordleGuess, WordleFeedback, WordleFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: WordleGameManager = WordleGameManager(
                word_list_file=Path("./data/wordle/words.txt"), seed=seed
            )

        @override
        def create_player(self) -> WordleManualPlayer:
            return WordleManualPlayer()

        @override
        def create_game(self) -> WordleGame:
            return self._game_manager.create_game(
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def format_final_result(self, *, final_result: WordleFinalResult) -> Iterator[str]:
            yield from WordleFinalResultFormatter.format_final_result(final_result=final_result)

    return WordleManualGym(seed=seed)


def build_letroso_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.letroso.common import (
        LetrosoFeedback,
        LetrosoFinalResult,
        LetrosoGuess,
        LetrosoInfo,
    )
    from word_arena.games.letroso.formatter import LetrosoFinalResultFormatter
    from word_arena.games.letroso.game import LetrosoGame, LetrosoGameManager
    from word_arena.games.letroso.players.manual import LetrosoManualPlayer

    class LetrosoManualGym(
        BaseManualGym[LetrosoInfo, None, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: LetrosoGameManager = LetrosoGameManager(
                word_list_file=Path("./data/letroso/words.txt"), seed=seed
            )

        @override
        def create_player(self) -> LetrosoManualPlayer:
            return LetrosoManualPlayer()

        @override
        def create_game(self) -> LetrosoGame:
            return self._game_manager.create_game(
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_letters=int(input("Max Input Letters: ")),
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def format_final_result(self, *, final_result: LetrosoFinalResult) -> Iterator[str]:
            yield from LetrosoFinalResultFormatter.format_final_result(final_result=final_result)

    return LetrosoManualGym(seed=seed)


def build_conexo_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from word_arena.games.conexo.common import (
        ConexoFeedback,
        ConexoFinalResult,
        ConexoGuess,
        ConexoInfo,
    )
    from word_arena.games.conexo.formatter import ConexoFinalResultFormatter
    from word_arena.games.conexo.game import ConexoGame, ConexoGameManager
    from word_arena.games.conexo.players.manual import ConexoManualPlayer

    class ConexoManualGym(
        BaseManualGym[ConexoInfo, None, ConexoGuess, ConexoFeedback, ConexoFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ConexoGameManager = ConexoGameManager(
                games_dir=Path("./data/conexo/games"), seed=seed
            )

        @override
        def create_player(self) -> ConexoManualPlayer:
            return ConexoManualPlayer()

        @override
        def create_game(self) -> ConexoGame:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def format_final_result(self, *, final_result: ConexoFinalResult) -> Iterator[str]:
            yield from ConexoFinalResultFormatter.format_final_result(final_result=final_result)

    return ConexoManualGym(seed=seed)


MANUAL_GYM_BUILDERS: dict[str, Callable[[int], BaseManualGym]] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
    "letroso": build_letroso_manual_gym,
    "conexo": build_conexo_manual_gym,
}


def main():
    from time import time_ns

    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index + 1}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: ")) - 1]](time_ns()).play()


if __name__ == "__main__":
    main()
