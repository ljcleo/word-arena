from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from .common import Analysis, GameRecord, GameSummary, Reflection, Turn


class BaseMemory[IT, HT, GT, FT, RT, ET](ABC):
    def __init__(self) -> None:
        self._history: list[GameSummary[IT, HT, GT, FT, RT]] = []

    @property
    def experience(self) -> ET:
        return self._experience

    @property
    def game_info(self) -> IT:
        return self._game_info

    @property
    def num_guesses(self) -> int:
        return len(self._trajectory)

    @property
    def current_trajectory(self) -> Iterator[Turn[HT, GT, FT]]:
        yield from self._trajectory

    def init_experience(self) -> None:
        self._experience: ET = self.create_experience()

    def prepare(self, *, game_info: IT) -> None:
        self._game_info: IT = game_info
        self._trajectory: list[Turn[HT, GT, FT]] = []
        self._latest_analysis: Analysis | None = None

    def digest(self, *, hint: HT, analysis: Analysis | None, guess: GT, feedback: FT) -> None:
        self._trajectory.append(Turn(hint=hint, guess=guess, feedback=feedback))
        self._latest_analysis = analysis

    def reflect(self, *, final_result: RT, update_experience: bool) -> None:
        record: GameRecord[IT, HT, GT, FT, RT] = GameRecord(
            game_info=self.game_info,
            trajectory=self._trajectory,
            latest_analysis=self._latest_analysis,
            final_result=final_result,
        )

        self._history.append(
            GameSummary(record=record, reflection=self.create_reflection(record=record))
        )

        if update_experience:
            self._experience = self.update_experience(
                history=self._history, old_experience=self.experience
            )

            self._history.clear()

    @abstractmethod
    def create_experience(self) -> ET:
        raise NotImplementedError()

    @abstractmethod
    def create_reflection(self, *, record: GameRecord[IT, HT, GT, FT, RT]) -> Reflection:
        raise NotImplementedError()

    @abstractmethod
    def update_experience(
        self, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]], old_experience: ET
    ) -> ET:
        raise NotImplementedError()
