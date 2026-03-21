from collections.abc import Callable

from .....common.llm.base import BaseLLM
from .....players.agent.player import AgentPlayer
from .....players.agent.preset import make_llm_engine_log_renderer
from ...common import NumberleFeedback, NumberleFinalResult, NumberleGuess, NumberleInfo
from ...players.agent.common import NumberleNote
from ...players.agent.engine.llm import NumberleLLMAgentEngine
from ...players.agent.renderer.log import NumberleLogAgentRenderer

llm_engine_log_renderer: Callable[
    [BaseLLM, bool, Callable[[str, str], None]],
    AgentPlayer[NumberleInfo, NumberleGuess, NumberleFeedback, NumberleFinalResult, NumberleNote],
] = make_llm_engine_log_renderer(
    engine_cls=NumberleLLMAgentEngine, renderer_cls=NumberleLogAgentRenderer
)
