from collections.abc import Iterator

from pydantic import BaseModel

from ....common.game.common import Trajectory


class AgentPrompter[IT, GT: BaseModel, FT, RT]:
    def __init__(self, *, guess_cls: type[GT]) -> None:
        self._guess_cls: type[GT] = guess_cls

    @abstractmethod
    def get_guess_detail(self, *, trajectory: Trajectory[IT, GT, FT]) -> str: ...

    @abstractmethod
    def get_guess_example(self, *, trajectory: Trajectory[IT, GT, FT]) -> GT: ...

    @abstractmethod
    def prompt_game_info(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT | None
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_guess(
        self,
        *,
        trajectory: Trajectory[IT, GT, FT],
        turn_id: int,
        guess: GT,
        final_result: RT | None,
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_feedback(
        self,
        *,
        trajectory: Trajectory[IT, GT, FT],
        turn_id: int,
        guess: GT,
        feedback: FT,
        final_result: RT | None,
    ) -> Iterator[tuple[str, str]]: ...

    @abstractmethod
    def prompt_final_result(
        self, *, trajectory: Trajectory[IT, GT, FT], final_result: RT
    ) -> Iterator[tuple[str, str]]: ...
