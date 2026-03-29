from importlib import import_module
from types import ModuleType
from typing import Any

from common import LLM_CONFIG_PATH, log
from pydantic import BaseModel
from utils import make_cls_prefix, try_validate

from word_arena.common.llm.engine.base import BaseLLMEngine
from word_arena.common.llm.llm import LLM
from word_arena.common.llm.renderer.log import LogLLMRenderer


class LLMConfig(BaseModel):
    type: str
    config: dict[str, Any]


def build_llm(*, llm_key: str) -> LLM:
    with (LLM_CONFIG_PATH / f"{llm_key}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read(), strict=True)

    prefix: str = make_cls_prefix(key=config.type)
    module: ModuleType = import_module(f"word_arena.llms.{config.type}")
    config_cls: type[BaseModel] = getattr(module, f"{prefix}LLMConfig")
    engine_cls: type[BaseLLMEngine] = getattr(module, f"{prefix}LLMEngine")
    engine: BaseLLMEngine = engine_cls(config=try_validate(cls=config_cls, data=config.config))

    if config.type == "manual_input":
        from word_arena.llms.manual_input import ManualInputLLMEngine

        assert isinstance(engine, ManualInputLLMEngine)
        engine.input_func = input

    return LLM(engine=engine, renderer=LogLLMRenderer(llm_log_func=log))
