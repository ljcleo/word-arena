from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import ContextoHintLLMAgentEngine
from ...players.agent.renderer.log import ContextoHintLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[ContextoHintLLMAgentEngine, ContextoHintLogAgentRenderer]:
    return (
        ContextoHintLLMAgentEngine(model=model, do_analyze=do_analyze),
        ContextoHintLogAgentRenderer(agent_log_func=log_func),
    )
