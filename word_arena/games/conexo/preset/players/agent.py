from collections.abc import Callable

from .....common.llm.llm import LLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import ConexoFeedback, ConexoFinalResult, ConexoGuess, ConexoInfo
from ...players.agent.common import ConexoNote
from ...players.agent.engine.llm import ConexoLLMAgentEngine
from ...players.agent.renderer.log import ConexoLogAgentRenderer

llm_engine_log_renderer: Callable[
    [LLM, bool, Callable[[str, str], None]],
    AgentPlayer[ConexoInfo, ConexoGuess, ConexoFeedback, ConexoFinalResult, ConexoNote],
] = make_llm_engine_log_renderer(
    engine_cls=ConexoLLMAgentEngine, renderer_cls=ConexoLogAgentRenderer
)
