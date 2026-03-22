from collections.abc import Callable

from pydantic import BaseModel

from ...common.llm.llm import LLM
from .engine.llm import BaseLLMAgentEngine
from .player import AgentPlayer
from .renderer.log import BaseLogAgentRenderer


def make_llm_engine_log_renderer[IT, GT: BaseModel, FT, RT, NT: BaseModel](
    *,
    engine_cls: type[BaseLLMAgentEngine[IT, GT, FT, RT, NT]],
    renderer_cls: type[BaseLogAgentRenderer[IT, GT, FT, RT, NT]],
) -> Callable[[LLM, bool, Callable[[str, str], None]], AgentPlayer[IT, GT, FT, RT, NT]]:
    def llm_engine_log_renderer(
        model: LLM, do_analyze: bool, log_func: Callable[[str, str], None]
    ) -> AgentPlayer[IT, GT, FT, RT, NT]:
        return AgentPlayer(
            engine=engine_cls(model=model, do_analyze=do_analyze),
            renderer=renderer_cls(agent_log_func=log_func),
        )

    return llm_engine_log_renderer
