from collections.abc import Callable

from .....common.llm.base import BaseLLM
from ...players.agent.engine.llm import WordleLLMAgentEngine
from ...players.agent.renderer.log import WordleLogAgentRenderer


def llm_engine_log_renderer(
    *, model: BaseLLM, do_analyze: bool, log_func: Callable[[str, str], None]
) -> tuple[WordleLLMAgentEngine, WordleLogAgentRenderer]:
    return (
        WordleLLMAgentEngine(model=model, do_analyze=do_analyze),
        WordleLogAgentRenderer(agent_log_func=log_func),
    )
