from collections.abc import Callable

from .....common.llm.llm import LLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import WordleFeedback, WordleFinalResult, WordleGuess, WordleInfo
from ...players.agent.common import WordleNote
from ...players.agent.engine.llm import WordleLLMAgentEngine
from ...players.agent.renderer.log import WordleLogAgentRenderer

llm_engine_log_renderer: Callable[
    [LLM, bool, Callable[[str, str], None]],
    AgentPlayer[WordleInfo, WordleGuess, WordleFeedback, WordleFinalResult, WordleNote],
] = make_llm_engine_log_renderer(
    engine_cls=WordleLLMAgentEngine, renderer_cls=WordleLogAgentRenderer
)
