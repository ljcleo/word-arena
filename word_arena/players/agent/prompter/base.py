from abc import ABC, abstractmethod
from collections.abc import Iterator

from pydantic import BaseModel

from ....common.game.common import Trajectory


class BaseAgentPrompterPromptConfig(BaseModel):
    role_definition: str
    game_rule: str
    note_detail: str
    reflection_detail: str


class BaseAgentPrompter[PT: BaseAgentPrompterPromptConfig, IT, GT, FT, RT](ABC):
    GUESS_CLS: type[GT]

    def __init__(self, *, prompt_config: PT) -> None:
        self._prompt_config: PT = prompt_config

    @property
    def prompt_config(self) -> PT:
        return self._prompt_config

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
