from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any

class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def list_models(self) -> List[str]:
        """Retorna la lista de modelos disponibles para el proveedor."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **opts: Any) -> str:
        """Ejecuta una respuesta de conversación síncrona."""
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], **opts: Any) -> AsyncIterator[str]:
        """Envía la respuesta mediante un generador asíncrono para Server-Sent Events."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Verifica conectividad con el proveedor."""
        pass

