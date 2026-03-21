from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import ContextoHintFeedback, ContextoHintGuess
from ...players.agent.common import ContextoHintNote
from ...players.agent.engine.llm import ContextoHintLLMAgentEngine
from ...players.agent.renderer.log import ContextoHintLogAgentRenderer

llm_engine_log_renderer: Callable[
    [BaseLLM, bool, Callable[[str, str], None]],
    AgentPlayer[list[str], ContextoHintGuess, ContextoHintFeedback, list[str], ContextoHintNote],
] = make_llm_engine_log_renderer(
    engine_cls=ContextoHintLLMAgentEngine, renderer_cls=ContextoHintLogAgentRenderer
)
