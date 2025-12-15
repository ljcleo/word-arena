from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypedDict

from pydantic import BaseModel

from common.game import GameResult
from llm.common import BaseLLM, Message


class GameRecord[GT, PT, AT, RT, FT, MT: BaseModel, TT: BaseModel](TypedDict):
    game_result: GameResult[GT, PT, tuple[MT, AT], RT, FT]
    reflection: TT | None


class BaseMemory[GT, PT, AT, RT, FT, MT: BaseModel, TT: BaseModel, ET: BaseModel](ABC):
    def __init__(
        self, model: BaseLLM, reflection_type: type[TT], experience_type: type[ET]
    ) -> None:
        self._model: BaseLLM = model
        self._reflection_type: type[TT] = reflection_type
        self._experience_type: type[ET] = experience_type
        self._history: list[GameRecord[GT, PT, AT, RT, FT, MT, TT]] = []

    @property
    def game_info(self) -> GT:
        return self._game_info

    @property
    def experience(self) -> ET:
        return self._experience

    @property
    def current_trajectory(self) -> Iterator[tuple[PT, tuple[MT, AT], RT]]:
        yield from self._trajectory

    def prepare(self, *, game_info: GT) -> None:
        self._game_info: GT = game_info
        self._trajectory: list[tuple[PT, tuple[MT, AT], RT]] = []
        self.process_game_info(game_info=game_info)

        self._experience: ET = self._model.parse(
            *self.make_create_experience_messages(), format=self._experience_type
        )

    def update_analysis(self, *, analysis: MT) -> None:
        self._latest_analysis: MT = analysis

    def digest(self, *, hint: PT, guess: AT, result: RT) -> None:
        self._trajectory.append((hint, (self._latest_analysis, guess), result))

    def reflect(self, *, summary: FT, update_experience: bool) -> None:
        game_result: GameResult[GT, PT, tuple[MT, AT], RT, FT] = {
            "game_info": self._game_info,
            "trajectory": self._trajectory,
            "summary": summary,
        }

        reflection: TT = self._model.parse(
            *self.make_reflection_messages(game_result=game_result), format=self._reflection_type
        )

        print(f"Reflection: {reflection}")

        self._history.append({"game_result": game_result, "reflection": reflection})

        if update_experience:
            self._experience = self._model.parse(
                *self.make_update_experience_messages(history=self._history),
                format=self._experience_type,
            )

            print("New Experience:", self._experience, sep="\n\n")

            self._history.clear()

    @abstractmethod
    def process_game_info(self, *, game_info: GT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def make_create_experience_messages(self) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_reflection_messages(
        self, *, game_result: GameResult[GT, PT, tuple[MT, AT], RT, FT]
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_update_experience_messages(
        self, *, history: list[GameRecord[GT, PT, AT, RT, FT, MT, TT]]
    ) -> Iterator[Message]:
        raise NotImplementedError()
