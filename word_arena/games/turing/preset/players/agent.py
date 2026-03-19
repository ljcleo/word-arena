from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import TuringLLMAgentEngine
from ...players.agent.renderer.log import TuringLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[TuringLLMAgentEngine, TuringLogAgentRenderer]:
    return (
        TuringLLMAgentEngine(model=model, do_analyze=do_analyze),
        TuringLogAgentRenderer(agent_log_func=log_func),
    )
