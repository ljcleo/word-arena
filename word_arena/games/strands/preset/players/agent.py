from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import StrandsFeedback, StrandsFinalResult, StrandsGuess, StrandsInfo
from ...players.agent.common import StrandsNote
from ...players.agent.engine.llm import StrandsLLMAgentEngine
from ...players.agent.renderer.log import StrandsLogAgentRenderer

llm_engine_log_renderer: Callable[
    [BaseLLM, bool, Callable[[str, str], None]],
    AgentPlayer[StrandsInfo, StrandsGuess, StrandsFeedback, StrandsFinalResult, StrandsNote],
] = make_llm_engine_log_renderer(
    engine_cls=StrandsLLMAgentEngine, renderer_cls=StrandsLogAgentRenderer
)
