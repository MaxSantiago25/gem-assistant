import httpx
from typing import AsyncIterator, List, Dict, Any
from app.connections.base import LLMProvider

class LMStudioProvider(LLMProvider):
    name = "lmstudio"

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url.rstrip("/")

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/models")
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/models")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("id") for m in data.get("data", [])]
        except Exception:
            pass
        return []

    async def chat(self, messages: List[Dict[str, str]], **opts: Any) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "messages": messages,
                "stream": False,
                **opts
            }
            res = await client.post(f"{self.base_url}/chat/completions", json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, messages: List[Dict[str, str]], **opts: Any) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "messages": messages,
                "stream": True,
                **opts
            }
            async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:].strip()
                        if chunk == "[DONE]":
                            break
                        yield chunk

