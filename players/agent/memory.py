from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TypedDict

from pydantic import BaseModel

from llm.common import BaseLLM, Message


class Analysis(BaseModel):
    analysis: str
    plan: str

    @staticmethod
    def example() -> Analysis:
        return Analysis(analysis="...", plan="...")

    @staticmethod
    def example_str() -> str:
        return Analysis.example().model_dump_json()


class Turn[PT, AT, RT](TypedDict):
    hint: PT
    analysis: Analysis | None
    guess: AT
    result: RT


class Reflection(BaseModel):
    summary: str
    lessons: str

    @staticmethod
    def example() -> Reflection:
        return Reflection(summary="In this trial, ...", lessons="...")

    @staticmethod
    def example_str() -> str:
        return Reflection.example().model_dump_json()


class GameRecord[GT, PT, AT, RT, FT](TypedDict):
    game_info: GT
    trajectory: list[Turn[PT, AT, RT]]
    summary: FT
    reflection: Reflection


class BaseMemory[GT, PT, AT, RT, FT, ET: BaseModel](ABC):
    def __init__(self, model: BaseLLM, experience_type: type[ET]) -> None:
        self._model: BaseLLM = model
        self._experience_type: type[ET] = experience_type
        self._history: list[GameRecord[GT, PT, AT, RT, FT]] = []

        self._experience: ET = self._model.parse(
            *self.make_create_experience_messages(), format=self._experience_type
        )

        print("Initial Experience:", self._experience, sep="\n\n")

    @property
    def game_info(self) -> GT:
        return self._game_info

    @property
    def experience(self) -> ET:
        return self._experience

    @property
    def num_guesses(self) -> int:
        return len(self._trajectory)

    @property
    def current_trajectory(self) -> Iterator[Turn[PT, AT, RT]]:
        yield from self._trajectory

    def prepare(self, *, game_info: GT) -> None:
        self._game_info: GT = game_info
        self._trajectory: list[Turn[PT, AT, RT]] = []
        self.process_game_info(game_info=game_info)

    def digest(self, *, hint: PT, analysis: Analysis | None, guess: AT, result: RT) -> None:
        self._trajectory.append(
            {"hint": hint, "analysis": analysis, "guess": guess, "result": result}
        )

    def reflect(self, *, summary: FT, update_experience: bool) -> None:
        reflection: Reflection = self._model.parse(
            *self.make_reflection_messages(
                game_info=self.game_info, trajectory=self.current_trajectory, summary=summary
            ),
            format=Reflection,
        )

        print(f"Reflection: {reflection}")

        self._history.append(
            {
                "game_info": self._game_info,
                "trajectory": list(self.current_trajectory),
                "summary": summary,
                "reflection": reflection,
            }
        )

        if update_experience:
            self._experience = self._model.parse(
                *self.make_update_experience_messages(history=self._history),
                format=self._experience_type,
            )

            print("New Experience:", self._experience, sep="\n\n")
            self._history.clear()

    @abstractmethod
    def make_create_experience_messages(self) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def process_game_info(self, *, game_info: GT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def make_reflection_messages(
        self, *, game_info: GT, trajectory: Iterable[Turn[PT, AT, RT]], summary: FT
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_update_experience_messages(
        self, *, history: list[GameRecord[GT, PT, AT, RT, FT]]
    ) -> Iterator[Message]:
        raise NotImplementedError()
