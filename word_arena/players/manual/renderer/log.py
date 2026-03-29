from collections.abc import Iterator
from typing import Any, override

from ....common.player.renderer.log import BaseLogPlayerRenderer


class ManualLogPlayerRenderer(BaseLogPlayerRenderer[None, None, Any, None, Any, Any, Any, None]):
    def __init__(self) -> None:
        super().__init__(player_log_func=lambda *_: None, prompt_config=None)

    @override
    def format_note(self, *, note: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    def format_analysis(self, *, analysis: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    def format_reflection(self, *, reflection: None) -> Iterator[tuple[str, str]]:
        yield from ()
