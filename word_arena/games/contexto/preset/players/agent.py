from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import ContextoFeedback, ContextoFinalResult, ContextoGuess
from ...players.agent.common import ContextoNote
from ...players.agent.engine.llm import ContextoLLMAgentEngine
from ...players.agent.renderer.log import ContextoLogAgentRenderer

llm_engine_log_renderer: Callable[
    [BaseLLM, bool, Callable[[str, str], None]],
    AgentPlayer[int, ContextoGuess, ContextoFeedback, ContextoFinalResult, ContextoNote],
] = make_llm_engine_log_renderer(
    engine_cls=ContextoLLMAgentEngine, renderer_cls=ContextoLogAgentRenderer
)
