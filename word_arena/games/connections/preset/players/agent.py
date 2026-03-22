from collections.abc import Callable

from .....common.llm.llm import LLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import ConnectionsFeedback, ConnectionsFinalResult, ConnectionsGuess, ConnectionsInfo
from ...players.agent.common import ConnectionsNote
from ...players.agent.engine.llm import ConnectionsLLMAgentEngine
from ...players.agent.renderer.log import ConnectionsLogAgentRenderer

llm_engine_log_renderer: Callable[
    [LLM, bool, Callable[[str, str], None]],
    AgentPlayer[
        ConnectionsInfo,
        ConnectionsGuess,
        ConnectionsFeedback,
        ConnectionsFinalResult,
        ConnectionsNote,
    ],
] = make_llm_engine_log_renderer(
    engine_cls=ConnectionsLLMAgentEngine, renderer_cls=ConnectionsLogAgentRenderer
)
