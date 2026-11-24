from typing import Dict, Optional
from app.connections.base import LLMProvider
from app.connections.llm.llamacpp import LlamaCppProvider
from app.connections.llm.lmstudio import LMStudioProvider
from app.connections.llm.gemini import GeminiProvider

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {
            "llamacpp": LlamaCppProvider(),
            "lmstudio": LMStudioProvider(),
            "gemini": GeminiProvider()
        }
        self._active_provider_name = "llamacpp"

    def register(self, provider: LLMProvider):
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[LLMProvider]:
        return self._providers.get(name)

    def get_active(self) -> LLMProvider:
        return self._providers.get(self._active_provider_name, self._providers["llamacpp"])

    def set_active(self, name: str):
        if name in self._providers:
            self._active_provider_name = name

    def list_available(self) -> list[str]:
        return list(self._providers.keys())

registry = ProviderRegistry()
