import os
import httpx
from typing import AsyncIterator, List, Dict, Any, Optional
from app.connections.base import LLMProvider

class LlamaCppProvider(LLMProvider):
    name = "llamacpp"

    def __init__(self, host: str = "127.0.0.1", port: Optional[int] = None, api_key: Optional[str] = None):
        self.host = host
        self.port = port or int(os.environ.get("LLAMA_PORT", 8080))
        self.api_key = api_key or os.environ.get("LLAMA_API_KEY", "dev-llama-key")
        self.base_url = f"http://{self.host}:{self.port}/v1"

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def health(self) -> bool:
        """Verifica disponibilidad de llama-server."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """Lista los modelos disponibles en el directorio del router."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("id") for m in data.get("data", [])]
        except Exception:
            pass
        return []

    async def chat(self, messages: List[Dict[str, str]], model: str = "gemma-4-E4B-it-qat", **opts: Any) -> str:
        """Envía petición síncrona a llama-server."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **opts
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=self._get_headers(), json=payload)
                if res.status_code == 404:
                    raise RuntimeError("MODELO_NO_ENCONTRADO")
                if res.status_code == 500:
                    err_text = res.text.lower()
                    if "out of memory" in err_text or "cuda" in err_text or "vram" in err_text:
                        raise RuntimeError("VRAM_INSUFICIENTE")
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError("LOCAL_NO_DISPONIBLE")

    async def stream(self, messages: List[Dict[str, str]], model: str = "gemma-4-E4B-it-qat", **opts: Any) -> AsyncIterator[str]:
        """Envía respuesta en streaming SSE desde llama-server."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **opts
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.base_url}/chat/completions", headers=self._get_headers(), json=payload) as response:
                    if response.status_code == 404:
                        raise RuntimeError("MODELO_NO_ENCONTRADO")
                    if response.status_code == 500:
                        raise RuntimeError("VRAM_INSUFICIENTE")
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:].strip()
                            if chunk == "[DONE]":
                                break
                            yield chunk
        except httpx.ConnectError:
            raise RuntimeError("LOCAL_NO_DISPONIBLE")

