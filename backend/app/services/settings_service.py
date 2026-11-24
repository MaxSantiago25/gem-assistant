from typing import Dict, Any
from app.repositories.settings_repo import settings_repo, SettingsRepository

class SettingsService:
    def __init__(self, repo: SettingsRepository = settings_repo):
        self.repo = repo

    def get_settings(self) -> Dict[str, Any]:
        return self.repo.get_all()

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        self.repo.update_many(new_settings)
        return self.repo.get_all()

settings_service = SettingsService()

