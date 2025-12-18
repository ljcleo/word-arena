from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from pydantic import BaseModel

from llm.common import BaseLLM, Message


class Analysis(BaseModel):
    past_analysis_summary: str
    current_analysis: str
    plan: str

    def __str__(self) -> str:
        return "\n".join(
            (
                f"Past analysis summary: {self.past_analysis_summary}",
                f"Analysis update: {self.current_analysis}",
                f"Plan: {self.plan}",
            )
        )

    @staticmethod
    def example() -> Analysis:
        return Analysis(past_analysis_summary="...", current_analysis="...", plan="...")


class Turn[PT, AT, RT](BaseModel):
    hint: PT
    guess: AT
    result: RT


class Reflection(BaseModel):
    summary: str
    lessons: str

    @staticmethod
    def example() -> Reflection:
        return Reflection(summary="In this trial, ...", lessons="...")

    @staticmethod
    def example_json() -> str:
        return Reflection.example().model_dump_json()


class GameRecord[GT, PT, AT, RT, FT](BaseModel):
    game_info: GT
    trajectory: list[Turn[PT, AT, RT]]
    latest_analysis: Analysis | None
    summary: FT


class GameSummary[GT, PT, AT, RT, FT](BaseModel):
    record: GameRecord[GT, PT, AT, RT, FT]
    reflection: Reflection


class BaseMemory[GT, PT, AT, RT, FT, ET: BaseModel](ABC):
    def __init__(self, model: BaseLLM, experience_type: type[ET]) -> None:
        self._model: BaseLLM = model
        self._experience_type: type[ET] = experience_type
        self._history: list[GameSummary[GT, PT, AT, RT, FT]] = []

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
        self._latest_analysis: Analysis | None = None

    def digest(self, *, hint: PT, analysis: Analysis | None, guess: AT, result: RT) -> None:
        self._trajectory.append(Turn(hint=hint, guess=guess, result=result))
        self._latest_analysis = analysis

    def reflect(self, *, summary: FT, update_experience: bool) -> None:
        record: GameRecord[GT, PT, AT, RT, FT] = GameRecord(
            game_info=self.game_info,
            trajectory=self._trajectory,
            latest_analysis=self._latest_analysis,
            summary=summary,
        )

        reflection: Reflection = self._model.parse(
            *self.make_reflection_messages(record=record),
            format=Reflection,
        )

        print(f"Reflection: {reflection}")
        self._history.append(GameSummary(record=record, reflection=reflection))

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
    def make_reflection_messages(
        self, *, record: GameRecord[GT, PT, AT, RT, FT]
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_update_experience_messages(
        self, *, history: list[GameSummary[GT, PT, AT, RT, FT]]
    ) -> Iterator[Message]:
        raise NotImplementedError()
