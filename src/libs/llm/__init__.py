"""
LLM Module.

This package contains LLM client abstractions and implementations:
- Base LLM class (text-only)
- LLM factory
- Provider implementations (OpenAI, Azure, Ollama, DeepSeek)
"""

from src.libs.llm.base_llm import BaseLLM, ChatResponse, Message
from src.libs.llm.llm_factory import LLMFactory
from src.libs.llm.openai_llm import OpenAILLM, OpenAILLMError
from src.libs.llm.azure_llm import AzureLLM, AzureLLMError
from src.libs.llm.deepseek_llm import DeepSeekLLM, DeepSeekLLMError
from src.libs.llm.ollama_llm import OllamaLLM, OllamaLLMError

# Register text-only LLM providers with factory
LLMFactory.register_provider("openai", OpenAILLM)
LLMFactory.register_provider("azure", AzureLLM)
LLMFactory.register_provider("deepseek", DeepSeekLLM)
LLMFactory.register_provider("ollama", OllamaLLM)

__all__ = [
    # Base classes
    "BaseLLM",
    # Data types
    "ChatResponse",
    "Message",
    # Factory
    "LLMFactory",
    # Text-only LLM implementations
    "OpenAILLM",
    "OpenAILLMError",
    "AzureLLM",
    "AzureLLMError",
    "DeepSeekLLM",
    "DeepSeekLLMError",
    "OllamaLLM",
    "OllamaLLMError",
]
