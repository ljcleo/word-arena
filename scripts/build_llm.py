from collections.abc import Callable
from typing import Any

from common import log

from word_arena.common.llm.base import BaseLLM


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


def build_llm(*, llm_key: str, config: dict[str, Any]) -> BaseLLM:
    return LLM_BUILDERS[llm_key](config)
