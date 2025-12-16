from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TypedDict

from pydantic import BaseModel

from llm.common import BaseLLM, Message


class Turn[PT, MT: BaseModel, AT, RT](TypedDict):
    hint: PT
    analysis: MT | None
    guess: AT
    result: RT


class GameRecord[GT, PT, MT: BaseModel, AT, RT, FT, TT: BaseModel](TypedDict):
    game_info: GT
    trajectory: list[Turn[PT, MT, AT, RT]]
    summary: FT
    reflection: TT


class BaseMemory[GT, PT, MT: BaseModel, AT, RT, FT, TT: BaseModel, ET: BaseModel](ABC):
    def __init__(
        self, model: BaseLLM, reflection_type: type[TT], experience_type: type[ET]
    ) -> None:
        self._model: BaseLLM = model
        self._reflection_type: type[TT] = reflection_type
        self._experience_type: type[ET] = experience_type
        self._history: list[GameRecord[GT, PT, MT, AT, RT, FT, TT]] = []

    @property
    def game_info(self) -> GT:
        return self._game_info

    @property
    def experience(self) -> ET:
        return self._experience

    @property
    def current_trajectory(self) -> Iterator[Turn[PT, MT, AT, RT]]:
        yield from self._trajectory

    def prepare(self, *, game_info: GT) -> None:
        self._game_info: GT = game_info
        self._trajectory: list[Turn[PT, MT, AT, RT]] = []
        self.process_game_info(game_info=game_info)

        self._experience: ET = self._model.parse(
            *self.make_create_experience_messages(), format=self._experience_type
        )

    def digest(self, *, hint: PT, analysis: MT | None, guess: AT, result: RT) -> None:
        self._trajectory.append(
            {"hint": hint, "analysis": analysis, "guess": guess, "result": result}
        )

    def reflect(self, *, summary: FT, update_experience: bool) -> None:
        reflection: TT = self._model.parse(
            *self.make_reflection_messages(
                game_info=self.game_info, trajectory=self.current_trajectory, summary=summary
            ),
            format=self._reflection_type,
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
    def process_game_info(self, *, game_info: GT) -> None:
        raise NotImplementedError()

    @abstractmethod
    def make_create_experience_messages(self) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_reflection_messages(
        self, *, game_info: GT, trajectory: Iterable[Turn[PT, MT, AT, RT]], summary: FT
    ) -> Iterator[Message]:
        raise NotImplementedError()

    @abstractmethod
    def make_update_experience_messages(
        self, *, history: list[GameRecord[GT, PT, MT, AT, RT, FT, TT]]
    ) -> Iterator[Message]:
        raise NotImplementedError()
