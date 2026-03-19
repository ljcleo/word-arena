from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import ContextoLLMAgentEngine
from ...players.agent.renderer.log import ContextoLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[ContextoLLMAgentEngine, ContextoLogAgentRenderer]:
    return (
        ContextoLLMAgentEngine(model=model, do_analyze=do_analyze),
        ContextoLogAgentRenderer(agent_log_func=log_func),
    )
