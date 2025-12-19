from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import override

from common.game import BaseGame
from players.manual import BaseManualPlayer


class BaseManualGym[IT, HT, GT, FT, RT](ABC):
    def play(self) -> None:
        player: BaseManualPlayer[IT, HT, GT, FT] = self.create_player()
        final_result: RT = self.create_game().play(player=player)
        print("You Guessed", player.num_guesses, "Times")
        self.report_final_result(final_result=final_result)

    @abstractmethod
    def create_player(self) -> BaseManualPlayer[IT, HT, GT, FT]:
        raise NotImplementedError()

    @abstractmethod
    def create_game(self) -> BaseGame[IT, HT, GT, FT, RT]:
        raise NotImplementedError()

    @abstractmethod
    def report_final_result(self, *, final_result: RT) -> None:
        raise NotImplementedError()


def build_contexto_manual_gym(seed: int) -> BaseManualGym:
    from games.contexto.common import ContextoFeedback, ContextoFinalResult
    from games.contexto.game import ContextoGameManager
    from games.contexto.players.manual import ContextoManualPlayer

    class ContextoManualGym(BaseManualGym[int, None, str, ContextoFeedback, ContextoFinalResult]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ContextoGameManager = ContextoGameManager(seed=seed)

        @override
        def create_player(self) -> BaseManualPlayer[int, None, str, ContextoFeedback]:
            return ContextoManualPlayer()

        @override
        def create_game(self) -> BaseGame[int, None, str, ContextoFeedback, ContextoFinalResult]:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def report_final_result(self, *, final_result: ContextoFinalResult) -> None:
            print("Best Position:", final_result.best_pos + 1)
            print("Top Words:", *final_result.top_words[:10])

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

        @override
        def create_player(self) -> BaseManualPlayer[None, list[str], int, int]:
            return ContextoHintManualPlayer()

        @override
        def create_game(self) -> BaseGame[None, list[str], int, int, list[str]]:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), num_candidates=int(input("Number of Candidates: "))
            )

        @override
        def report_final_result(self, *, final_result: list[str]) -> None:
            print("Top Words:", *final_result[:10])

    return ContextoHintManualGym(seed=seed)


def build_wordle_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from games.wordle.common import WordleFeedback, WordleFinalResult, WordleInfo
    from games.wordle.game import WordleGameManager
    from games.wordle.players.manual import WordleManualPlayer

    class WordleManualGym(BaseManualGym[WordleInfo, None, str, WordleFeedback, WordleFinalResult]):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: WordleGameManager = WordleGameManager(
                word_list_file=Path("./data/wordle/words.txt"), seed=seed
            )

        @override
        def create_player(self) -> BaseManualPlayer[WordleInfo, None, str, WordleFeedback]:
            return WordleManualPlayer()

        @override
        def create_game(self) -> BaseGame[WordleInfo, None, str, WordleFeedback, WordleFinalResult]:
            return self._game_manager.create_game(
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def report_final_result(self, *, final_result: WordleFinalResult) -> None:
            print("Found", final_result.num_found, "word(s)")
            print("Answer:", *final_result.answers)

    return WordleManualGym(seed=seed)


def build_letroso_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from games.letroso.common import LetrosoFeedback, LetrosoFinalResult, LetrosoInfo
    from games.letroso.game import LetrosoGameManager
    from games.letroso.players.manual import LetrosoManualPlayer

    class LetrosoManualGym(
        BaseManualGym[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: LetrosoGameManager = LetrosoGameManager(
                word_list_file=Path("./data/letroso/words.txt"), seed=seed
            )

        @override
        def create_player(self) -> BaseManualPlayer[LetrosoInfo, None, str, LetrosoFeedback]:
            return LetrosoManualPlayer()

        @override
        def create_game(
            self,
        ) -> BaseGame[LetrosoInfo, None, str, LetrosoFeedback, LetrosoFinalResult]:
            return self._game_manager.create_game(
                target_ids=[
                    int(input(f"Word ID {i + 1}: ")) for i in range(int(input("Num Targets: ")))
                ],
                max_letters=int(input("Max Input Letters: ")),
                max_guesses=int(input("Max Guesses: ")),
            )

        @override
        def report_final_result(self, *, final_result: LetrosoFinalResult) -> None:
            print("Found", final_result.num_found, "word(s)")
            print("Answer:", *final_result.answers)

    return LetrosoManualGym(seed=seed)


def build_conexo_manual_gym(seed: int) -> BaseManualGym:
    from pathlib import Path

    from games.conexo.common import ConexoFeedback, ConexoFinalResult, ConexoInfo
    from games.conexo.game import ConexoGameManager
    from games.conexo.players.manual import ConexoManualPlayer

    class ConexoManualGym(
        BaseManualGym[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult]
    ):
        def __init__(self, *, seed: int) -> None:
            self._game_manager: ConexoGameManager = ConexoGameManager(
                games_dir=Path("./data/conexo/games"), seed=seed
            )

        @override
        def create_player(self) -> BaseManualPlayer[ConexoInfo, None, set[int], ConexoFeedback]:
            return ConexoManualPlayer()

        @override
        def create_game(
            self,
        ) -> BaseGame[ConexoInfo, None, set[int], ConexoFeedback, ConexoFinalResult]:
            return self._game_manager.create_game(
                game_id=int(input("Game ID: ")), max_guesses=int(input("Max Guesses: "))
            )

        @override
        def report_final_result(self, *, final_result: ConexoFinalResult) -> None:
            print("Found", final_result.num_found, "Group(s)")
            print("All Groups:")

            for group in final_result.groups:
                print(f"- {group.theme}:", *group.words)

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
