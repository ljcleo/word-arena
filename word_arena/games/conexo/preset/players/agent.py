from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import ConexoLLMAgentEngine
from ...players.agent.renderer.log import ConexoLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[ConexoLLMAgentEngine, ConexoLogAgentRenderer]:
    return (
        ConexoLLMAgentEngine(model=model, do_analyze=do_analyze),
        ConexoLogAgentRenderer(agent_log_func=log_func),
    )
