from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from ...players.agent.engine.llm import RedactleLLMAgentEngine
from ...players.agent.renderer.log import RedactleLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> AgentPlayer:
    return AgentPlayer(
        engine=RedactleLLMAgentEngine(model=model, do_analyze=do_analyze),
        renderer=RedactleLogAgentRenderer(agent_log_func=log_func),
    )
