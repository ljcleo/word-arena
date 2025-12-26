from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from ..game.common import GameRecord, Turn
from .common import Analysis, GameSummary, Reflection


class BaseMemory[IT, HT, GT, FT, RT, NT](ABC):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._history: list[GameSummary[IT, HT, GT, FT, RT]] = []

    @property
    def note(self) -> NT:
        return self._note

    @property
    def game_info(self) -> IT:
        return self._game_info

    @property
    def num_guesses(self) -> int:
        return len(self._trajectory)

    @property
    def current_trajectory(self) -> Iterator[Turn[HT, GT, FT]]:
        yield from self._trajectory

    def init_note(self) -> None:
        self._note: NT = self.create_note()

    def prepare(self, *, game_info: IT) -> None:
        self._game_info: IT = game_info
        self._trajectory: list[Turn[HT, GT, FT]] = []
        self._latest_analysis: Analysis | None = None

    def digest(self, *, hint: HT, analysis: Analysis | None, guess: GT, feedback: FT) -> None:
        self._trajectory.append(Turn(hint=hint, guess=guess, feedback=feedback))
        self._latest_analysis = analysis

    def reflect(self, *, game_record: GameRecord[IT, HT, GT, FT, RT], update_note: bool) -> None:
        self._history.append(
            GameSummary(
                game_record=game_record,
                latest_analysis=self._latest_analysis,
                reflection=self.create_reflection(
                    game_record=game_record, latest_analysis=self._latest_analysis
                ),
            )
        )

        if update_note:
            self._note = self.update_note(history=self._history, note=self.note)
            self._history.clear()

    @abstractmethod
    def create_note(self) -> NT:
        raise NotImplementedError()

    @abstractmethod
    def create_reflection(
        self, *, game_record: GameRecord[IT, HT, GT, FT, RT], latest_analysis: Analysis | None
    ) -> Reflection:
        raise NotImplementedError()

    @abstractmethod
    def update_note(self, *, history: Iterable[GameSummary[IT, HT, GT, FT, RT]], note: NT) -> NT:
        raise NotImplementedError()
