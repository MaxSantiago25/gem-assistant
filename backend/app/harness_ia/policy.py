import json
import os
from pathlib import Path
from typing import List, Dict, Any

POLICY_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "harness_policy.json"
APPS_FILE = Path(__file__).resolve().parent.parent.parent / "config" / "apps.json"

class PolicyError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code

class HarnessPolicy:
    def __init__(self, policy_path: Path = POLICY_FILE, apps_path: Path = APPS_FILE):
        self.policy_path = policy_path
        self.apps_path = apps_path
        self._policy = self._load_policy()
        self._apps = self._load_apps()

    def _load_policy(self) -> Dict[str, Any]:
        if self.policy_path.exists():
            try:
                with open(self.policy_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[HarnessPolicy] Error cargando política: {e}")
        return {
            "permitted_zones": [
                r"%USERPROFILE%\Downloads",
                r"%USERPROFILE%\Documents",
                r"%USERPROFILE%\Desktop"
            ],
            "forbidden_zones": [
                r"C:\Windows",
                r"C:\Program Files",
                r"C:\Program Files (x86)",
                r"C:\ProgramData",
                r"%USERPROFILE%\.ssh",
                r"%APPDATA%\IslandAgent"
            ],
            "blocked_extensions": [
                ".exe", ".bat", ".cmd", ".ps1", ".msi", ".vbs", ".scr", ".js", ".lnk", ".com", ".dll"
            ],
            "limits": {
                "max_batch_operations": 50,
                "max_hourly_operations": 100
            },
            "auto_approve": {
                "fs_mkdir": False
            }
        }

    def _load_apps(self) -> Dict[str, Any]:
        if self.apps_path.exists():
            try:
                with open(self.apps_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("apps", {})
            except Exception as e:
                print(f"[HarnessPolicy] Error cargando apps: {e}")
        return {}

    def get_permitted_zones(self) -> List[Path]:
        raw_zones = self._policy.get("permitted_zones", [])
        return [Path(os.path.realpath(os.path.expandvars(z))) for z in raw_zones]

    def get_forbidden_zones(self) -> List[Path]:
        raw_zones = self._policy.get("forbidden_zones", [])
        return [Path(os.path.realpath(os.path.expandvars(z))) for z in raw_zones]

    def is_extension_blocked(self, filename: str) -> bool:
        ext = Path(filename).suffix.lower()
        blocked = self._policy.get("blocked_extensions", [])
        return ext in blocked

    def get_limits(self) -> Dict[str, int]:
        return self._policy.get("limits", {"max_batch_operations": 50, "max_hourly_operations": 100})

    def get_app(self, app_id: str) -> Dict[str, Any]:
        return self._apps.get(app_id)

policy = HarnessPolicy()

