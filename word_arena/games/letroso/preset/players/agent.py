from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import LetrosoFeedback, LetrosoFinalResult, LetrosoGuess, LetrosoInfo
from ...players.agent.common import LetrosoNote
from ...players.agent.engine.llm import LetrosoLLMAgentEngine
from ...players.agent.renderer.log import LetrosoLogAgentRenderer

llm_engine_log_renderer: Callable[
    [BaseLLM, bool, Callable[[str, str], None]],
    AgentPlayer[LetrosoInfo, LetrosoGuess, LetrosoFeedback, LetrosoFinalResult, LetrosoNote],
] = make_llm_engine_log_renderer(
    engine_cls=LetrosoLLMAgentEngine, renderer_cls=LetrosoLogAgentRenderer
)
