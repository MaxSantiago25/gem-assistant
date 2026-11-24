import os
from typing import AsyncIterator, List, Dict, Any
from app.connections.base import LLMProvider

class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = model_name

    async def health(self) -> bool:
        return bool(self.api_key)

    async def list_models(self) -> List[str]:
        return ["gemini-2.5-flash", "gemini-2.5-pro"]

    async def chat(self, messages: List[Dict[str, str]], **opts: Any) -> str:
        # La implementación completa usará google-genai en Fase 4
        return "Respuesta simulada de Gemini"

    async def stream(self, messages: List[Dict[str, str]], **opts: Any) -> AsyncIterator[str]:
        yield "Respuesta "
        yield "en streaming "
        yield "de Gemini."

