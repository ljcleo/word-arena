from collections.abc import Callable

from .....common.llm.llm import LLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import RedactleFeedback, RedactleFinalResult, RedactleGuess, RedactleInfo
from ...players.agent.common import RedactleNote
from ...players.agent.engine.llm import RedactleLLMAgentEngine
from ...players.agent.renderer.log import RedactleLogAgentRenderer

llm_engine_log_renderer: Callable[
    [LLM, bool, Callable[[str, str], None]],
    AgentPlayer[RedactleInfo, RedactleGuess, RedactleFeedback, RedactleFinalResult, RedactleNote],
] = make_llm_engine_log_renderer(
    engine_cls=RedactleLLMAgentEngine, renderer_cls=RedactleLogAgentRenderer
)
