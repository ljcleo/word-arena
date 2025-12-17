from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from common.game import BaseGame
from players.manual import BaseManualPlayer


class BaseManualGym[GT, PT, AT, RT, FT](ABC):
    def play(self) -> None:
        player: BaseManualPlayer[GT, PT, AT, RT] = self.create_player()
        summary: FT = self.create_game().play(player=player)
        print("You Guessed", player.num_guesses, "Times")
        self.summarize(summary=summary)

    @abstractmethod
    def create_player(self) -> BaseManualPlayer[GT, PT, AT, RT]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self) -> BaseGame[GT, PT, AT, RT, FT]:
        raise NotImplementedError()

    @abstractmethod
    def summarize(self, *, summary: FT) -> None:
        raise NotImplementedError()


def build_contexto_manual_gym(seed: int) -> BaseManualGym:
    from games.contexto.common import ContextoResult
    from games.contexto.game import ContextoGameManager
    from games.contexto.players.manual import ContextoManualPlayer

    class ContextoManualGym(BaseManualGym[int, None, str, ContextoResult, list[str]]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ContextoGameManager = ContextoGameManager(seed=seed)
            self._max_guesses: int = int(input("Max Guesses: "))

        @override
        def create_player(self) -> BaseManualPlayer[int, None, str, ContextoResult]:
            return ContextoManualPlayer()

        @override
        def create_game(self) -> BaseGame[int, None, str, ContextoResult, list[str]]:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")), max_guesses=self._max_guesses
            )

        @override
        def summarize(self, *, summary: list[str]) -> None:
            print("Top Words:", *summary[:10])

    return ContextoManualGym(seed=seed)


def build_contexto_hint_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from games.contexto_hint.game import ContextoHintGameManager
    from games.contexto_hint.players.manual import ContextoHintManualPlayer

    class ContextoHintManualGym(BaseManualGym[None, list[str], int, int, list[str]]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ContextoHintGameManager = ContextoHintGameManager(
                games_dir=Path("./data/contexto_hint/games"), seed=seed
            )

            self._num_candidates: int = int(input("Number of Candidates: "))

        @override
        def create_player(self) -> BaseManualPlayer[None, list[str], int, int]:
            return ContextoHintManualPlayer()

        @override
        def create_game(self) -> BaseGame[None, list[str], int, int, list[str]]:
            return self._game_manager.create_game(
                game_id=int(input("Input Game ID: ")), num_candidates=self._num_candidates
            )

        @override
        def summarize(self, *, summary: list[str]) -> None:
            print("Top Words:", *summary[:10])

    return ContextoHintManualGym(seed=seed)


def build_wordle_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from games.wordle.common import WordleInfo, WordleResult
    from games.wordle.game import WordleGameManager
    from games.wordle.players.manual import WordleManualPlayer

    class WordleManualGym(BaseManualGym[WordleInfo, None, str, WordleResult, list[str]]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: WordleGameManager = WordleGameManager(
                word_list_file=Path("./data/wordle/words.txt"), seed=seed
            )

        @override
        def create_player(self) -> BaseManualPlayer[WordleInfo, None, str, WordleResult]:
            return WordleManualPlayer()

        @override
        def create_game(self) -> BaseGame[WordleInfo, None, str, WordleResult, list[str]]:
            return self._game_manager.create_game(
                target_ids=[
                    int(input(f"Input Word {i + 1} ID: "))
                    for i in range(int(input("Num Targets: ")))
                ],
                max_accept_guesses=int(input("Max Accept Guesses: ")),
            )

        @override
        def summarize(self, *, summary: list[str]) -> None:
            print("Answer:", *summary)

    return WordleManualGym(seed=seed)


MANUAL_GYM_BUILDERS: dict[str, Callable[[int], BaseManualGym]] = {
    "contexto": build_contexto_manual_gym,
    "contexto-hint": build_contexto_hint_manual_gym,
    "wordle": build_wordle_manual_gym,
}


def main():
    from time import time_ns

    games: list[str] = list(MANUAL_GYM_BUILDERS.keys())
    for index, game in enumerate(games):
        print(f"{index + 1}. {game}")

    MANUAL_GYM_BUILDERS[games[int(input("Game Index: ")) - 1]](time_ns()).play()


if __name__ == "__main__":
    main()
