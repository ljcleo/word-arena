from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from ..game.common import GameRecord, Turn
from .common import Analysis, GameSummary, Reflection


class BaseMemory[IT, HT, GT, FT, RT, ET](ABC):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
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

    def reflect(
        self, *, game_record: GameRecord[IT, HT, GT, FT, RT], update_experience: bool
    ) -> None:
        self._history.append(
            GameSummary(
                game_record=game_record,
                latest_analysis=self._latest_analysis,
                reflection=self.create_reflection(
                    game_record=game_record, latest_analysis=self._latest_analysis
                ),
            )
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
    def create_reflection(
        self, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Reflection:
        raise NotImplementedError()

    @abstractmethod
    def update_experience(
        self, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]], old_experience: ET
    ) -> ET:
        raise NotImplementedError()
