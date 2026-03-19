from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import StrandsLLMAgentEngine
from ...players.agent.renderer.log import StrandsLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[StrandsLLMAgentEngine, StrandsLogAgentRenderer]:
    return (
        StrandsLLMAgentEngine(model=model, do_analyze=do_analyze),
        StrandsLogAgentRenderer(agent_log_func=log_func),
    )
