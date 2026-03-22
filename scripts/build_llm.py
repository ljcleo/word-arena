from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from common import log, make_cls_prefix
from pydantic import BaseModel

from word_arena.common.llm.engine.base import BaseLLMEngine
from word_arena.common.llm.llm import LLM
from word_arena.common.llm.renderer.log import LogLLMRenderer

LLM_CONFIG_PATH: Path = Path("./config/llms")


class LLMConfig(BaseModel):
    type: str
    config: dict[str, Any]


def build_llm(*, llm_key: str) -> LLM:
    with (LLM_CONFIG_PATH / f"{llm_key}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read())

    prefix: str = make_cls_prefix(key=config.type)
    module: ModuleType = import_module(f"word_arena.llms.{config.type}")
    config_cls: type[BaseModel] = getattr(module, f"{prefix}LLMConfig")
    engine_cls: type[BaseLLMEngine] = getattr(module, f"{prefix}LLMEngine")

    return LLM(
        engine=engine_cls(config=config_cls.model_validate(config.config)),
        renderer=LogLLMRenderer(llm_log_func=log),
    )
