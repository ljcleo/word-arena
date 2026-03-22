from collections.abc import Callable
from pathlib import Path
from typing import Any

from common import log
from pydantic import BaseModel

from word_arena.common.llm.base import BaseLLM

LLM_CONFIG_PATH: Path = Path("./config/llms")


class LLMConfig(BaseModel):
    type: str
    config: dict[str, Any]


def build_pseudo_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.pseudo import PseudoLLM, PseudoLLMConfig

    return PseudoLLM(config=PseudoLLMConfig.model_validate(config), llm_log_func=log)


def build_openai_chat_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.openai_chat import OpenaiChatLLM, OpenaiChatLLMConfig

    return OpenaiChatLLM(config=OpenaiChatLLMConfig.model_validate(config))


def build_openai_responses_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.openai_responses import OpenaiResponsesLLM, OpenaiResponsesLLMConfig

    return OpenaiResponsesLLM(config=OpenaiResponsesLLMConfig.model_validate(config))


def build_anthropic_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.anthropic import AnthropicLLM, AnthropicLLMConfig

    return AnthropicLLM(config=AnthropicLLMConfig.model_validate(config), llm_log_func=log)


def build_google_llm(config: dict[str, Any]) -> BaseLLM:
    from word_arena.llms.google import GoogleLLM, GoogleLLMConfig

    return GoogleLLM(config=GoogleLLMConfig.model_validate(config), llm_log_func=log)


LLM_BUILDERS: dict[str, Callable[[dict[str, Any]], BaseLLM]] = {
    "pseudo": build_pseudo_llm,
    "openai-chat": build_openai_chat_llm,
    "openai-responses": build_openai_responses_llm,
    "anthropic": build_anthropic_llm,
    "google": build_google_llm,
}


def build_llm(*, llm_key: str) -> BaseLLM:
    with (LLM_CONFIG_PATH / f"{llm_key}.json").open("rb") as f:
        config: LLMConfig = LLMConfig.model_validate_json(f.read())

    return LLM_BUILDERS[config.type](config.config)
