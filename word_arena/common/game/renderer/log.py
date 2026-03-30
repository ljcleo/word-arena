from abc import ABC
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, override

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, TypeAdapter
from ruamel.yaml import YAML

from ..state import GameStateInterface
from .base import BaseGameRenderer


class LogGameRenderer[IT, GT, FT, RT](BaseGameRenderer[IT, GT, FT, RT], ABC):
    def __init__(self, *, game_log_func: Callable[[str, str], None], template_path: Path) -> None:
        self._game_log_func: Callable[[str, str], None] = game_log_func

        self._jinja: Environment = Environment(
            loader=FileSystemLoader(template_path), autoescape=select_autoescape()
        )

    @override
    def render_game_info(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self._format("game_info", game_info=state.game_info))

    @override
    def render_guess(self, *, state: GameStateInterface[IT, GT, FT, RT], guess: GT) -> None:
        self._log(*self._format("guess", trajectory=state.trajectory, guess=guess))

    @override
    def render_last_feedback(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(*self._format("last_feedback", trajectory=state.trajectory))

    @override
    def render_final_result(self, *, state: GameStateInterface[IT, GT, FT, RT]) -> None:
        self._log(
            ("Total Guesses", str(len(state.turns))),
            *self._format(
                "final_result", trajectory=state.trajectory, final_result=state.final_result
            ),
        )

    def _format(self, prefix: str, /, **kwargs: Any) -> Iterator[tuple[str, str]]:
        class Pair(BaseModel):
            key: str
            value: str

        for pair in TypeAdapter(list[Pair]).validate_python(
            YAML(typ="safe").load(
                self._jinja.get_template(f"{prefix}.yaml.jinja2").render(**kwargs)
            ),
            strict=True,
        ):
            yield pair.key, pair.value

    def _log(self, *output: tuple[str, str]):
        for key, value in output:
            self._game_log_func(key, value)
