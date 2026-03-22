from collections.abc import Callable

from .....common.llm.llm import LLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import TuringFeedback, TuringFinalResult, TuringGuess, TuringInfo
from ...players.agent.common import TuringNote
from ...players.agent.engine.llm import TuringLLMAgentEngine
from ...players.agent.renderer.log import TuringLogAgentRenderer

llm_engine_log_renderer: Callable[
    [LLM, bool, Callable[[str, str], None]],
    AgentPlayer[TuringInfo, TuringGuess, TuringFeedback, TuringFinalResult, TuringNote],
] = make_llm_engine_log_renderer(
    engine_cls=TuringLLMAgentEngine, renderer_cls=TuringLogAgentRenderer
)
