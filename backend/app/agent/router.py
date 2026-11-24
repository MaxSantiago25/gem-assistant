import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "models.json"

class ModelRouter:
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ModelRouter] Error cargando models.json: {e}")
        return {
            "profiles": {
                "rapido": {"provider": "llamacpp", "model": "gemma-4-E4B-it-qat", "ctx": 8192},
                "herramientas": {"provider": "llamacpp", "model": "qwen3.5-9b", "ctx": 8192},
                "nube": {"provider": "gemini", "model": "gemini-2.5-flash"}
            },
            "routing": {
                "chat": "rapido",
                "redaccion": "rapido",
                "acciones_pc": "herramientas",
                "tareas": "herramientas",
                "correo_resumen": "rapido"
            },
            "privacy": {
                "correo": "solo_local",
                "mipc": "solo_local",
                "chat": "nube_con_permiso"
            }
        }

    def resolve_profile(self, task_type: str) -> str:
        """Determina el perfil según el tipo de tarea (ARQUITECTURA-IA.md §4)."""
        routing = self._config.get("routing", {})
        return routing.get(task_type, "rapido")

    def get_profile_config(self, profile: str) -> Dict[str, Any]:
        """Obtiene la configuración del perfil."""
        profiles = self._config.get("profiles", {})
        return profiles.get(profile, profiles.get("rapido", {}))

    def allows_cloud(self, task_type: str, user_granted_permission: bool = False) -> bool:
        """Evalúa si la tarea tiene permitido escalar a la nube según las reglas de privacidad."""
        privacy_rule = self._config.get("privacy", {}).get(task_type, "solo_local")
        if privacy_rule == "solo_local":
            return False
        if privacy_rule == "nube_con_permiso":
            return user_granted_permission
        if privacy_rule == "nube_libre":
            return True
        return False

router = ModelRouter()

