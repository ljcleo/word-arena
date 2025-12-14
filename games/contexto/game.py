from datetime import date
from random import Random
from typing import override

import httpx

from common.game import BaseGame, GameResult
from games.contexto.common import ContextoError, ContextoResponse

type ContextoGameResult = GameResult[None, None, str, ContextoResponse | ContextoError, list[str]]


class ContextoGame(BaseGame[None, None, str, ContextoResponse | ContextoError, list[str]]):
    def __init__(self, *, game_id: int) -> None:
        self._game_id: int = game_id
        self._base_url: str = "https://api.contexto.me/machado/en"

    @override
    def start_game(self) -> None:
        self._best_pos: int = 1 << 32

    @override
    def is_win(self) -> bool:
        return self._best_pos == 0

    @override
    def get_guess_prompt(self) -> None:
        pass

    @override
    def process_guess(self, *, guess: str) -> ContextoResponse | ContextoError:
        if not (guess.isalpha() and guess.islower()):
            return ContextoError(error="Your guess should only contain lowercase letters")

        try:
            response: httpx.Response = httpx.get(f"{self._base_url}/game/{self._game_id}/{guess}")
        except Exception:
            raise

        if response.status_code == 200:
            try:
                result: ContextoResponse = ContextoResponse.model_validate_json(response.content)
            except Exception as e:
                return ContextoError(error=f"Cannot parse 200: {e}")

            self._best_pos = min(self._best_pos, result.distance)
            return result
        elif response.status_code == 404:
            try:
                return ContextoError.model_validate_json(response.content)
            except Exception as e:
                return ContextoError(error=f"Cannot parse 404: {e}")
        else:
            return ContextoError(error=f"Status code {response.status_code}")

    @override
    def summarize_game(self) -> list[str]:
        try:
            return httpx.get(f"{self._base_url}/top/{self._game_id}").json()["words"]
        except Exception:
            raise


class ContextoGameManager:
    def __init__(self, *, seed: int) -> None:
        self._max_games: int = (date.today() - date(2022, 9, 18)).days
        self._rng: Random = Random(seed)

    def create_game(self, *, game_id: int | None) -> ContextoGame:
        if game_id is None:
            game_id = self._rng.randrange(self._max_games + 1)

        print("Current Game ID:", game_id)
        return ContextoGame(game_id=game_id)
