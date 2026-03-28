from collections.abc import Iterator
from typing import Any, override

from ....common.player.renderer.log import BaseLogPlayerRenderer


class ManualLogPlayerRenderer(BaseLogPlayerRenderer[None, Any, None, Any, Any, Any, None]):
    @override
    def format_note(self, *, note: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    def format_analysis(self, *, analysis: None) -> Iterator[tuple[str, str]]:
        yield from ()

    @override
    def format_reflection(self, *, reflection: None) -> Iterator[tuple[str, str]]:
        yield from ()
